#!/usr/bin/with-contenv bashio

if bashio::config.exists 'default_price_kwh'; then
  export DEFAULT_PRICE_KWH=$(bashio::config 'default_price_kwh')
fi
if bashio::config.exists 'ha_token'; then
  export HA_TOKEN=$(bashio::config 'ha_token')
fi
if bashio::config.exists 'ha_url'; then
  export HA_URL=$(bashio::config 'ha_url')
fi
export DATA_PATH="/data"
export INGRESS_PATH=$(bashio::addon.ingress_entry)

export APP_VERSION=$(bashio::addon.version)

bashio::log.info "Starting FV Manager on port 8010"
bashio::log.info "Ingress path: ${INGRESS_PATH}"
bashio::log.info "Data dir: ${DATA_PATH}"

export PYTHONPATH=/app/src

exec python3 -m uvicorn src.main:app \
  --host 0.0.0.0 \
  --port 8010 \
  --root-path "${INGRESS_PATH}"
