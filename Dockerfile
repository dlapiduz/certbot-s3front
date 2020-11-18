FROM python:3.6-alpine
ENTRYPOINT [ "certbot" ]

VOLUME /etc/letsencrypt /var/lib/letsencrypt
WORKDIR /opt/certbot

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
