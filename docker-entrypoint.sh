#!/bin/sh

/usr/local/bin/certbot -n --init --agree-tos -a s3front_auth -i s3front_installer --s3front_auth-s3-bucket $AWS_S3_BUCKET --s3front_installer-cf-distribution-id $AWS_DISTRIBUTION_ID --email $EMAIL -d $DOMAIN
