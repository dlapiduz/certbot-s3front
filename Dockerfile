FROM python:2-alpine
ENTRYPOINT [ "certbot" ]

VOLUME /etc/letsencrypt /var/lib/letsencrypt
WORKDIR /opt/certbot

RUN apk add --no-cache --virtual .certbot-deps \
    libffi \
    libssl1.0 \
    ca-certificates \
    binutils

RUN apk add --no-cache --virtual .build-deps \
    gcc \
    linux-headers \
    openssl-dev \
    musl-dev \
    libffi-dev \
    && pip install certbot-s3front \
    && apk del .build-deps
