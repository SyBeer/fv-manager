"""
Tests for services.ha_stats — HA Statistics-based monthly energy fetch.

Mocking strategy: monkeypatch ha_stats._AsyncClient with a MockClient class
that handles the async context manager protocol and routes get/post calls
to test-supplied handler functions.
"""
import json
import time
import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

import services.ha_stats as ha_stats
from services.ha_stats import get_monthly_energy, get_current_month_energy


# ── Mock infrastructure ────────────────────────────────────────────────────────

class MockResponse:
    def __init__(self, status_code: int = 200, data: dict | None = None):
        self.status_code = status_code
        self._data = data or {}
        self.text = json.dumps(self._data)

    def json(self) -> dict:
        return self._data


class MockClient:
    """Async context manager mock for httpx.AsyncClient."""

    def __init__(self, get_fn=None, post_fn=None, **_):
        self._get_fn = get_fn or (lambda url, **kw: MockResponse(status_code=404))
        self._post_fn = post_fn or (lambda url, **kw: MockResponse(status_code=404))

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass

    async def get(self, url, **kwargs):
        return self._get_fn(url)

    async def post(self, url, **kwargs):
        return self._post_fn(url, **kwargs)


def stats_body(entity_id: str, change: float, wrapped: bool = True) -> dict:
    """Build a Statistics API response body."""
    inner = {entity_id: [{"change": change, "state": 9999.0}]}
    return {"response": inner} if wrapped else inner


def default_get(url: str) -> MockResponse:
    """Default GET handler: timezone + kWh unit."""
    if "/config" in url:
        return MockResponse(data={"time_zone": "Europe/Warsaw"})
    if "/states/" in url:
        return MockResponse(data={"attributes": {"unit_of_measurement": "kWh"}})
    return MockResponse(status_code=404)


def wh_get(url: str) -> MockResponse:
    """GET handler: timezone + Wh unit (Solaredge-style)."""
    if "/config" in url:
        return MockResponse(data={"time_zone": "Europe/Warsaw"})
    if "/states/" in url:
        return MockResponse(data={"attributes": {"unit_of_measurement": "Wh"}})
    return MockResponse(status_code=404)


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_state(tmp_path, monkeypatch):
    """Reset module-level caches and env vars before each test."""
    ha_stats._tz_cache = None
    ha_stats._current_month_cache.clear()
    monkeypatch.setenv("SUPERVISOR_TOKEN", "test-supervisor-token")
    monkeypatch.delenv("HA_URL", raising=False)
    monkeypatch.delenv("HA_TOKEN", raising=False)
    monkeypatch.setenv("DATA_PATH", str(tmp_path))


# ── Tests ──────────────────────────────────────────────────────────────────────

async def test_closed_month_returns_kwh(monkeypatch):
    """Closed month: returns correct kWh from Statistics API 'change' field."""
    entity = "sensor.grid_consumed"

    def post_fn(url, **kw):
        return MockResponse(data=stats_body(entity, 150.5))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_monthly_energy(entity, 2026, 4)  # April — closed
    assert result == 150.5


async def test_current_month_returns_partial_delta(monkeypatch):
    """Current month: returns Statistics API 'change' which reflects data so far."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    entity = "sensor.solar"
    now = datetime.now(ZoneInfo("Europe/Warsaw"))

    def post_fn(url, **kw):
        return MockResponse(data=stats_body(entity, 335.0))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_monthly_energy(entity, now.year, now.month)
    assert result == 335.0


async def test_no_data_returns_none_not_zero(monkeypatch):
    """Empty statistics response returns None, not 0 — zeros would be misleading."""
    entity = "sensor.solar"

    def post_fn(url, **kw):
        return MockResponse(data={"response": {}})  # entity missing from response

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_monthly_energy(entity, 2026, 3)
    assert result is None


async def test_wh_sensor_converts_to_kwh(monkeypatch):
    """Konwersja Wh→kWh jest delegowana do HA przez units={energy: kWh}.

    Kod nie przelicza jednostek u siebie — prosi HA o dane od razu w kWh. Test
    sprawdza rzeczywistą odpowiedzialność kodu: że zapytanie zawiera parametr
    units, a wynik to wartość zwrócona przez HA (już przeliczona do kWh).
    """
    entity = "sensor.solaredge_lifetime_energy"
    captured = {}

    def post_fn(url, **kw):
        captured["json"] = kw.get("json")
        # HA, poproszony o units={energy: kWh}, zwraca dla czujnika Wh już 800 kWh.
        return MockResponse(data=stats_body(entity, 800.0))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(wh_get, post_fn))

    result = await get_monthly_energy(entity, 2026, 4)
    assert result == 800.0
    assert captured["json"]["units"] == {"energy": "kWh"}


async def test_kwh_sensor_not_converted(monkeypatch):
    """kWh sensor (e.g. Zamel MEW-01): value returned as-is."""
    entity = "sensor.electricity_meter_total_forward_active_energy"

    def post_fn(url, **kw):
        return MockResponse(data=stats_body(entity, 123.456))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_monthly_energy(entity, 2026, 4)
    assert result == 123.456


async def test_container_restart_does_not_affect_result(monkeypatch):
    """Container restart in mid-month: Statistics API always returns full month delta.

    Simulates restart by clearing all in-memory state (done by reset_state fixture).
    The API still returns the correct accumulated value from HA's persistent stats DB.
    """
    from datetime import datetime
    from zoneinfo import ZoneInfo

    entity = "sensor.solar"
    now = datetime.now(ZoneInfo("Europe/Warsaw"))

    # Module state is completely fresh (reset_state fixture cleared everything)
    assert ha_stats._tz_cache is None
    assert entity not in ha_stats._current_month_cache

    def post_fn(url, **kw):
        # HA's statistics DB always has the full month's delta regardless of restarts
        return MockResponse(data=stats_body(entity, 800.0))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_monthly_energy(entity, now.year, now.month)
    assert result == 800.0  # Full month delta, not a partial post-restart value


async def test_persistent_cache_for_closed_month(monkeypatch, tmp_path):
    """Closed month result persists to disk; second call skips the Statistics API."""
    entity = "sensor.solar"
    call_count = 0

    def post_fn(url, **kw):
        nonlocal call_count
        call_count += 1
        return MockResponse(data=stats_body(entity, 500.0))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    r1 = await get_monthly_energy(entity, 2026, 3)

    # Bypass timezone re-fetch on second call
    ha_stats._tz_cache = "Europe/Warsaw"
    r2 = await get_monthly_energy(entity, 2026, 3)

    assert r1 == 500.0
    assert r2 == 500.0
    assert call_count == 1  # Statistics API called only once; second from disk cache


async def test_current_month_cache_ttl(monkeypatch):
    """Current month uses 5-minute TTL; expired entry triggers a new fetch."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    entity = "sensor.solar"
    now = datetime.now(ZoneInfo("Europe/Warsaw"))
    call_count = 0

    def post_fn(url, **kw):
        nonlocal call_count
        call_count += 1
        return MockResponse(data=stats_body(entity, 335.0))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    r1 = await get_monthly_energy(entity, now.year, now.month)
    assert call_count == 1

    # Simulate cache expiry: backdate the timestamp beyond TTL
    ha_stats._current_month_cache[entity] = (335.0, time.monotonic() - (ha_stats.CACHE_TTL_CURRENT + 10))
    ha_stats._tz_cache = "Europe/Warsaw"

    r2 = await get_monthly_energy(entity, now.year, now.month)
    assert r2 == 335.0
    assert call_count == 2  # Cache expired → new fetch


async def test_api_error_returns_none(monkeypatch):
    """HTTP 500 from Statistics API → returns None, does not raise."""
    entity = "sensor.solar"

    def post_fn(url, **kw):
        return MockResponse(status_code=500)

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_monthly_energy(entity, 2026, 4)
    assert result is None


async def test_no_ha_config_returns_none(monkeypatch):
    """Missing connection config → returns None without crashing."""
    monkeypatch.delenv("SUPERVISOR_TOKEN", raising=False)
    monkeypatch.delenv("HA_URL", raising=False)
    monkeypatch.delenv("HA_TOKEN", raising=False)

    result = await get_monthly_energy("sensor.solar", 2026, 4)
    assert result is None


async def test_get_current_month_energy_delegates_to_monthly(monkeypatch):
    """get_current_month_energy calls get_monthly_energy for local current month."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    entity = "sensor.solar"
    ha_stats._tz_cache = "Europe/Warsaw"
    now_local = datetime.now(ZoneInfo("Europe/Warsaw"))

    def post_fn(url, **kw):
        return MockResponse(data=stats_body(entity, 750.0))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_current_month_energy(entity)
    assert result == 750.0


async def test_standalone_mode_uses_ha_url_and_token(monkeypatch):
    """Without SUPERVISOR_TOKEN, uses HA_URL + HA_TOKEN env vars (standalone mode)."""
    monkeypatch.delenv("SUPERVISOR_TOKEN", raising=False)
    monkeypatch.setenv("HA_URL", "http://homeassistant.local:8123")
    monkeypatch.setenv("HA_TOKEN", "long-lived-token-abc")

    entity = "sensor.solar"
    captured_url: list[str] = []

    def get_fn(url):
        captured_url.append(url)
        if "/config" in url:
            return MockResponse(data={"time_zone": "Europe/Warsaw"})
        if "/states/" in url:
            return MockResponse(data={"attributes": {"unit_of_measurement": "kWh"}})
        return MockResponse(status_code=404)

    def post_fn(url, **kw):
        return MockResponse(data=stats_body(entity, 200.0))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(get_fn, post_fn))

    result = await get_monthly_energy(entity, 2026, 4)
    assert result == 200.0
    # All requests went to the configured HA URL, not the Supervisor endpoint
    assert all("homeassistant.local" in u for u in captured_url)


async def test_response_without_response_wrapper(monkeypatch):
    """Statistics API response without 'response' key (older HA format) is handled."""
    entity = "sensor.solar"

    def post_fn(url, **kw):
        # No {"response": ...} wrapper — entity data at top level
        return MockResponse(data=stats_body(entity, 400.0, wrapped=False))

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_monthly_energy(entity, 2026, 4)
    assert result == 400.0


async def test_multiple_buckets_summed(monkeypatch):
    """Multiple stat entries (e.g. partial months) are summed into one delta."""
    entity = "sensor.solar"

    def post_fn(url, **kw):
        data = {"response": {entity: [
            {"change": 300.0, "state": 9300.0},
            {"change": 500.0, "state": 9800.0},
        ]}}
        return MockResponse(data=data)

    monkeypatch.setattr(ha_stats, "_AsyncClient", lambda **kw: MockClient(default_get, post_fn))

    result = await get_monthly_energy(entity, 2026, 4)
    assert result == 800.0
