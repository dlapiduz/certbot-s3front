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

The easiest way to install both the certbot client and the certbot-s3front plugin is:

  ```
  pip install certbot-s3front
  ```

#### Mac with Homebrew certbot?
  Installed certbot using Homebrew on Mac (as the official way to install on a Mac)? Install the plugin with:

  ```bash
  $(brew --prefix certbot)/libexec/bin/pip install certbot-s3front
  ```

  **Note:** You will need to re-install the plugin each time certbot is updated through Homebrew.

#### Mac with pip certbot?
  Alternatively, you can have a local set up for Python and we recommend a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and have both certbot and certbot-s3front installed via pip.
  You might also need to install `dialog`: `brew install dialog`.

#### Ubuntu?
  If you are in Ubuntu you will need to install `pip` and other libraries first:
  ```
  apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev zlib1g-dev dialog
  ```
  And then run `pip install certbot-s3front`.

### How to use it

To generate a certificate and install it in a CloudFront distribution:

```bash
AWS_ACCESS_KEY_ID="REPLACE_WITH_YOUR_KEY" \
AWS_SECRET_ACCESS_KEY="REPLACE_WITH_YOUR_SECRET" \
certbot --agree-tos -a s3front_auth \
--s3front_auth-s3-bucket REPLACE_WITH_YOUR_BUCKET_NAME \
[ --s3front_auth-s3-region your-bucket-region-name ] #(the default is us-east-1, unless you want to set it to something else, you can delete this line) \
[ --s3front_auth-s3-directory your-bucket-directory ] # (default is "") \
-i s3front_installer \
--s3front_installer-cf-distribution-id REPLACE_WITH_YOUR_CF_DISTRIBUTION_ID \
-d REPLACE_WITH_YOUR_DOMAIN
```

Follow the screen prompts and you should end up with the certificate in your
distribution. It may take a couple minutes to update.


### Automate renewal

To automate the renewal process without prompts (for example, with a monthly cron), you can add the certbot parameters `--renew-by-default --text`


### Using with Docker

To build a docker image of `certbot` with the `s3front` plugin, clone this repo and run:

```bash
docker build . -t certbot-s3front
```

Then export the environment variables to an `env.list` file:

```bash
echo AWS_ACCESS_KEY_ID=YOUR_ID >> env.list
echo AWS_SECRET_ACCESS_KEY=YOUR_KEY >> env.list
echo AWS_S3_BUCKET=YOUR_S3_BUCKET_NAME >> env.list
echo AWS_DISTRIBUTION_ID=YOUR_DISTRIBUTION_ID >> env.list
echo DOMAIN=YOUR_DOMAIN >> env.list
echo EMAIL=YOUR_EMAIL >> env.list
```

And finally run the docker image:

```bash
docker run --rm --name lets-encrypt -it \
    -v ./letsencrypt/:/etc/letsencrypt \
    --env-file env.list \
    certbot-s3front \
```
