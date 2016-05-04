## S3/CloudFront plugin for Let's Encrypt client

Use the letsencrypt client to generate and install a certificate to be used with
an AWS CloudFront distribution of an S3 bucket.

### Before you start

Follow a guide like this one [https://docs.aws.amazon.com/gettingstarted/latest/swh/website-hosting-intro.html](https://docs.aws.amazon.com/gettingstarted/latest/swh/website-hosting-intro.html)
to use S3 and CloudFront for static site hosting.

Once you are done you should have:

- A domain pointing to a CloudFront distribution that will use an S3 bucket for origin.
- Both HTTP and HTTPS traffic are enabled in the CloudFront Distrubtion. This is important for certificate validation, at least while you get your certificate.
- An IAM policy with the permissions needed for this plugin. A [sample policy](sample-aws-policy.json) has been provided.

### Setup

1. Install the letsencrypt client [https://letsencrypt.readthedocs.org/en/latest/using.html#installation](https://letsencrypt.readthedocs.org/en/latest/using.html#installation)

  ```
  pip install letsencrypt
  ```

1. Install the letsencrypt-s3front plugin

  ```
  pip install letsencrypt-s3front
  ```

### How to use it

To generate a certificate and install it in a CloudFront distribution:
```
AWS_ACCESS_KEY_ID="REPLACE_WITH_YOUR_KEY" \
AWS_SECRET_ACCESS_KEY="REPLACE_WITH_YOUR_SECRET" \
letsencrypt --agree-tos -a letsencrypt-s3front:auth \
--letsencrypt-s3front:auth-s3-bucket REPLACE_WITH_YOUR_BUCKET_NAME \
[ --letsencrypt-s3front:auth-s3-region REPLACE-WITH-YOUR-BUCKET-REGION ] (the default is us-east-1, unless you want to set it to something else, you can delete this line) \
-i letsencrypt-s3front:installer \
--letsencrypt-s3front:installer-cf-distribution-id REPLACE_WITH_YOUR_CF_DISTRIBUTION_ID \
-d REPLACE_WITH_YOUR_DOMAIN
```

Follow the screen prompts and you should end up with the certificate in your
distribution. It may take a couple minutes to update.

To automate the renewal process without prompts (for example, with a monthly cron), you can add the letsencrypt parameters --renew-by-default --text
