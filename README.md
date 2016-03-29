## S3/CloudFront plugin for Let's Encrypt client

Use the letsencrypt client to generate and install a certificate to be used with
an AWS CloudFront distribution of an S3 bucket.

### Before you start

Follow a guide like this one [https://docs.aws.amazon.com/gettingstarted/latest/swh/website-hosting-intro.html](https://docs.aws.amazon.com/gettingstarted/latest/swh/website-hosting-intro.html)
to use S3 and CloudFront for static site hosting.

Once you are done you should have a domain pointing to a CloudFront distribution
that will use an S3 bucket for origin. It is important for the certificate
validation that both HTTP and HTTPS traffic are enabled (at least while you get
  the certificate).
  
You can view an example IAM policy (sample-aws-policy.json) with the permissions needed for this plugin.

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
AWS_ACCESS_KEY_ID="your_key" \
AWS_SECRET_ACCESS_KEY="your_secret" \
letsencrypt --agree-tos -a letsencrypt-s3front:auth \
--letsencrypt-s3front:auth-s3-bucket the_bucket \
[ --letsencrypt-s3front:auth-s3-region your-bucket-region-name ] (default is us-east-1) \
[ --letsencrypt-s3front:auth-s3-directory your-bucket-directory ] (default is root) \
-i letsencrypt-s3front:installer \
--letsencrypt-s3front:installer-cf-distribution-id your_cf_distribution_id \
-d the_domain
```

Follow the screen prompts and you should end up with the certificate in your
distribution. It may take a couple minutes to update.

To automate the renewal process without prompts (for example, with a monthly cron), you can add the letsencrypt parameters --renew-by-default --text
