## S3/CloudFront plugin for [Certbot](https://certbot.eff.org/) client

Use the certbot client to generate and install a certificate to be used with
an AWS CloudFront distribution of an S3 bucket.

### Before you start

Follow a guide like this one [https://docs.aws.amazon.com/gettingstarted/latest/swh/website-hosting-intro.html](https://docs.aws.amazon.com/gettingstarted/latest/swh/website-hosting-intro.html)
to use S3 and CloudFront for static site hosting.

Once you are done you should have:

- A domain pointing to a CloudFront distribution that will use an S3 bucket for origin.
- Both HTTP and HTTPS traffic are enabled in the CloudFront Distrubtion. This is important for certificate validation, at least while you get your certificate.
- An IAM policy with the permissions needed for this plugin. A [sample policy](sample-aws-policy.json) has been provided.

Note: If you're setting up both an apex and a `www.` domain, they'll have a respective S3 bucket each. You'll need to update the IAM policy to include access to both buckets.

### Setup

1. Install the certbot client followin the instructions here [https://certbot.eff.org/](https://certbot.eff.org/)
1. Install the certbot-s3front plugin

  ```
  pip install certbot-s3front
  ```

### How to use it

To generate a certificate and install it in a CloudFront distribution:

```bash
AWS_ACCESS_KEY_ID="REPLACE_WITH_YOUR_KEY" \
AWS_SECRET_ACCESS_KEY="REPLACE_WITH_YOUR_SECRET" \
certbot --agree-tos -a certbot-s3front:auth \
--certbot-s3front:auth-s3-bucket REPLACE_WITH_YOUR_BUCKET_NAME \
[ --certbot-s3front:auth-s3-region your-bucket-region-name ] #(the default is us-east-1, unless you want to set it to something else, you can delete this line) \
[ --certbot-s3front:auth-s3-directory your-bucket-directory ] # (default is "") \
-i certbot-s3front:installer \
--certbot-s3front:installer-cf-distribution-id REPLACE_WITH_YOUR_CF_DISTRIBUTION_ID \
-d REPLACE_WITH_YOUR_DOMAIN
```

Follow the screen prompts and you should end up with the certificate in your
distribution. It may take a couple minutes to update.


### Automate renewal

To automate the renewal process without prompts (for example, with a monthly cron), you can add the certbot parameters `--renew-by-default --text`
