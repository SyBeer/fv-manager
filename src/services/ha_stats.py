"""
HA Statistics-based monthly energy fetch.

Public API
----------
get_monthly_energy(entity_id, year, month) -> Optional[float]
    Returns monthly kWh delta from HA long-term statistics.
    Returns None (never 0) when data is unavailable.

get_current_month_energy(entity_id) -> Optional[float]
    Returns delta for the current month in HA's local timezone.
"""
from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

import httpx

logger = logging.getLogger(__name__)

# Swapped in tests with a mock client class
_AsyncClient = httpx.AsyncClient

CACHE_TTL_CURRENT = 300.0  # seconds, for current-month in-memory cache

# Module-level state (reset between test runs)
_tz_cache: Optional[str] = None
_current_month_cache: dict[str, tuple[float, float]] = {}  # entity → (kWh, monotonic_ts)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _data_dir() -> Path:
    return Path(os.getenv("DATA_PATH", str(Path(__file__).parent.parent.parent / "data")))


def _cache_file() -> Path:
    return _data_dir() / "stats_cache.json"


def _ha_conn() -> tuple[str, str]:
    """Return (base_api_url, token).

    HA add-on mode: uses SUPERVISOR_TOKEN (injected when homeassistant_api: true).
    Standalone mode: uses HA_URL + HA_TOKEN env vars (set from addon config or .env).
    """
    sup = os.getenv("SUPERVISOR_TOKEN", "")
    if sup:
        return "http://supervisor/core/api", sup
    url = os.getenv("HA_URL", "").rstrip("/")
    token = os.getenv("HA_TOKEN", "")
    return (f"{url}/api" if url else ""), token


def _load_persistent_cache() -> dict:
    try:
        f = _cache_file()
        if f.exists():
            return json.loads(f.read_text())
    except Exception:
        pass
    return {}


def _save_persistent_cache(data: dict) -> None:
    try:
        _data_dir().mkdir(parents=True, exist_ok=True)
        _cache_file().write_text(json.dumps(data))
    except Exception as exc:
        logger.warning("Cannot save stats cache: %s", exc)


def _cache_key(entity_id: str, year: int, month: int) -> str:
    return f"{entity_id}:{year}:{month:02d}"


async def _fetch_ha_timezone(
    client: httpx.AsyncClient, base_url: str, token: str
) -> str:
    """Fetch HA server timezone from /api/config. Caches in module-level _tz_cache."""
    global _tz_cache
    if _tz_cache:
        return _tz_cache
    try:
        r = await client.get(
            f"{base_url}/config",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        if r.status_code == 200:
            name = r.json().get("time_zone") or "Europe/Warsaw"
            _tz_cache = name
            return name
    except Exception as exc:
        logger.warning("Cannot fetch HA timezone: %s", exc)
    return "Europe/Warsaw"


def _pick_bucket(stats: list, year: int, month: int, tz: ZoneInfo) -> Optional[float]:
    """Return the 'change' value from the bucket matching year/month in local time.

    HA may return multiple monthly buckets when UTC boundaries don't align with
    local midnight (e.g. Europe/Warsaw is UTC+1/UTC+2). We match by parsing each
    bucket's 'start' timestamp in local time and checking year/month.

    Falls back to summing all buckets if none matches (old behaviour, safe default).
    """
    for entry in stats:
        start_raw = entry.get("start") or ""
        try:
            start_dt = datetime.fromisoformat(start_raw)
            start_local = start_dt.astimezone(tz)
            if start_local.year == year and start_local.month == month:
                ch = entry.get("change")
                return float(ch) if ch is not None else None
        except Exception:
            # Fallback: string prefix match (no TZ suffix in older HA versions)
            if start_raw.startswith(f"{year}-{month:02d}"):
                ch = entry.get("change")
                return float(ch) if ch is not None else None

    # No matching bucket — sum all (defensive fallback)
    logger.warning("No bucket matched %d-%02d; summing all %d buckets", year, month, len(stats))
    total: Optional[float] = None
    for entry in stats:
        ch = entry.get("change")
        if ch is not None:
            total = (total or 0.0) + float(ch)
    return total


# ── Public API ─────────────────────────────────────────────────────────────────

async def get_monthly_energy(entity_id: str, year: int, month: int) -> Optional[float]:
    """Return monthly energy delta in kWh via HA long-term statistics.

    Uses POST /api/services/recorder/get_statistics?return_response.
    Time boundaries are computed in HA's local timezone (fetched from /api/config).
    Unit conversion (Wh → kWh) handled server-side via units: {energy: kWh}.

    Caching:
      - Closed months: persisted to DATA_PATH/stats_cache.json
      - Current month: in-memory with 5-minute TTL

    Returns None — never 0 — when data is unavailable.
    """
    import calendar

    base_url, token = _ha_conn()
    if not base_url or not token:
        logger.warning("HA not configured (missing SUPERVISOR_TOKEN / HA_URL+HA_TOKEN)")
        return None

    async with _AsyncClient(timeout=20) as client:
        tz_name = await _fetch_ha_timezone(client, base_url, token)
        tz = ZoneInfo(tz_name)
        now_local = datetime.now(tz)
        is_current = year == now_local.year and month == now_local.month

        # ── Cache lookup ───────────────────────────────────────────────────────
        if is_current:
            entry = _current_month_cache.get(entity_id)
            if entry and (time.monotonic() - entry[1]) < CACHE_TTL_CURRENT:
                logger.debug("Cache hit (current month) %s %d-%02d", entity_id, year, month)
                return entry[0]
        else:
            key = _cache_key(entity_id, year, month)
            cached = _load_persistent_cache().get(key)
            if cached is not None:
                logger.debug("Cache hit (persistent) %s %d-%02d", entity_id, year, month)
                return cached

        # ── Time boundaries in HA-local time (no tz suffix) ───────────────────
        start_local = datetime(year, month, 1, 0, 0, 0, tzinfo=tz)
        if is_current:
            end_local = now_local
        else:
            last_day = calendar.monthrange(year, month)[1]
            end_local = datetime(year, month, last_day, 23, 59, 59, tzinfo=tz)

        start_str = start_local.strftime("%Y-%m-%d %H:%M:%S")
        end_str = end_local.strftime("%Y-%m-%d %H:%M:%S")

        # ── Statistics API call ────────────────────────────────────────────────
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        try:
            r = await client.post(
                f"{base_url}/services/recorder/get_statistics",
                headers=headers,
                params={"return_response": "true"},
                json={
                    "start_time": start_str,
                    "end_time": end_str,
                    "statistic_ids": [entity_id],
                    "period": "month",
                    "types": ["change"],
                    "units": {"energy": "kWh"},
                },
                timeout=20,
            )
        except httpx.TimeoutException:
            logger.warning("Statistics API timeout %s %d-%02d", entity_id, year, month)
            return None
        except Exception as exc:
            logger.warning("Statistics API error %s: %s", entity_id, exc)
            return None

        if r.status_code != 200:
            logger.warning(
                "Statistics API %d for %s %d-%02d: %s",
                r.status_code, entity_id, year, month, r.text[:200],
            )
            return None

        try:
            body = r.json()
        except Exception as exc:
            logger.warning("Statistics API JSON parse error %s: %s", entity_id, exc)
            return None

        # services/…?return_response wraps in {"response": {entity_id: [...]}}
        inner = body.get("response")
        if inner is None:
            inner = body
        stats: list = inner.get(entity_id) or []

        if not stats:
            logger.warning("Empty statistics for %s in %d-%02d", entity_id, year, month)
            return None

        total = _pick_bucket(stats, year, month, tz)

        if total is None:
            logger.warning("No 'change' in statistics for %s %d-%02d", entity_id, year, month)
            return None

        result = round(total, 3)

        # ── Update cache ───────────────────────────────────────────────────────
        if is_current:
            _current_month_cache[entity_id] = (result, time.monotonic())
        else:
            persistent = _load_persistent_cache()
            persistent[_cache_key(entity_id, year, month)] = result
            _save_persistent_cache(persistent)

        return result


async def get_current_month_energy(entity_id: str) -> Optional[float]:
    """Return energy delta for the current month in HA's local timezone."""
    global _tz_cache
    base_url, token = _ha_conn()
    if not base_url or not token:
        return None

    if not _tz_cache:
        async with _AsyncClient(timeout=10) as client:
            await _fetch_ha_timezone(client, base_url, token)

    tz = ZoneInfo(_tz_cache or "Europe/Warsaw")
    now_local = datetime.now(tz)
    return await get_monthly_energy(entity_id, now_local.year, now_local.month)
