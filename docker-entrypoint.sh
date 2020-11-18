#!/bin/sh

/usr/local/bin/certbot -n --init --agree-tos -a certbot-s3front:auth -i certbot-s3front:installer --certbot-s3front:auth-s3-bucket $AWS_S3_BUCKET --certbot-s3front:installer-cf-distribution-id $AWS_DISTRIBUTION_ID --email $EMAIL -d $DOMAIN
