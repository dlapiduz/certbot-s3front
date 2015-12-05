## S3/CloudFront plugin for Let's Encrypt client

Use the letsencrypt client to generate and install a certificate to be used with
an AWS CloudFront distribution of an S3 bucket.

### Before you start

Follow a guide like this one [http://docs.aws.amazon.com/gettingstarted/latest/swh/website-hosting-intro.html][]
to use S3 and CloudFront for static site hosting.

Once you are done you should have a domain pointing to a CloudFront distribution
that will use an S3 bucket for origin. It is important for the certificate
validation that both HTTP and HTTPS traffic are enabled (at least while you get
  the certificate).

### Setup

1. Install the letsencrypt client [https://letsencrypt.readthedocs.org/en/latest/using.html#installation][]
1. Clone this repo locally: `git clone https://github.com/dlapiduz/letsencrypt-s3front.git`
1. Install it:
        ```
        cd letsencrypt-s3front
        python setup.py Install
        ```

### How to use it

To just download the certificate you need to run a command like this:
```
AWS_ACCESS_KEY_ID="your_key" \
AWS_SECRET_ACCESS_KEY="your_secret" \
S3_BUCKET="the_bucket" \
letsencrypt --agree-tos -a letsencrypt-s3front:s3front_authenticator \
-d your_domain.com certonly
