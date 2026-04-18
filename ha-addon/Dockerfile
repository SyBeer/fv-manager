ARG BUILD_FROM=ghcr.io/home-assistant/aarch64-base:3.20
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

COPY src/ /app/src/
COPY templates/ /app/templates/
COPY run.sh /run.sh
RUN chmod a+x /run.sh

WORKDIR /app
CMD ["/run.sh"]
