#!/usr/bin/with-contenv bashio

export DEFAULT_PRICE_KWH=$(bashio::config 'default_price_kwh')
export HA_TOKEN=$(bashio::config 'ha_token')
export HA_ENTITY=$(bashio::config 'ha_entity')
export DATA_PATH="/data"
export INGRESS_PATH=$(bashio::addon.ingress_entry)

bashio::log.info "Starting FV Manager on port 8010"
bashio::log.info "Ingress path: ${INGRESS_PATH}"
bashio::log.info "Data dir: ${DATA_PATH}"

export PYTHONPATH=/app/src

exec python3 -m uvicorn src.main:app \
  --host 0.0.0.0 \
  --port 8010 \
  --root-path "${INGRESS_PATH}"
