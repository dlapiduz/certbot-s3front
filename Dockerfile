FROM python:3.6-alpine

VOLUME /etc/letsencrypt /var/lib/letsencrypt
WORKDIR /opt/certbot

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

RUN apk add --no-cache --virtual .certbot-deps \
    libffi \
    libssl1.1 \
    ca-certificates \
    binutils

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    linux-headers \
    openssl-dev \
    musl-dev \
    libffi-dev \
    && pip install urllib3==1.25.11 \
    && pip install certbot-s3front \
    && apk del .build-deps


ENTRYPOINT [ "/usr/local/bin/docker-entrypoint.sh" ]
