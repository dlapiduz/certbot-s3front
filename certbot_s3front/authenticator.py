"""S3/CloudFront Let's Encrypt authenticator plugin."""
import os
import logging
import re
import subprocess

import zope.interface

import boto3

from acme import challenges

from certbot import errors
from certbot import interfaces
from certbot.plugins import common


logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(common.Plugin):
    description = "S3/CloudFront Authenticator"

    @classmethod
    def add_parser_arguments(cls, add):
        add("s3-bucket", default=os.getenv('S3_BUCKET'),
            help="Bucket referenced by CloudFront distribution")
        add("s3-region", default="us-east-1",
            help="Bucket region name")
        add("s3-access-key", default=os.getenv('AWS_ACCESS_KEY_ID'),
            help="Access key ID")
        add("s3-secret-key", default=os.getenv('AWS_SECRET_ACCESS_KEY'),
            help="Secret key ID")
        add("s3-directory",
            help="A directory of the S3 bucket/the distribution's origin path")

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self._httpd = None

    def prepare(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return ("")

    def get_chall_pref(self, domain):
        # pylint: disable=missing-docstring,no-self-use,unused-argument
        return [challenges.HTTP01]

    def _get_key(self, achall):   # pylint: disable=missing-docstring
        key = achall.chall.path[1:]
        s3_dir = self.conf('s3-directory')
        return '{0}/{1}'.format(s3_dir, key) if s3_dir else key

    def perform(self, achalls):  # pylint: disable=missing-docstring
        responses = []
        for achall in achalls:
            responses.append(self._perform_single(achall))
        return responses

    def _perform_single(self, achall):
        # upload the challenge file to the desired s3 bucket
        # then run simple http verification
        response, validation = achall.response_and_validation()
        session = boto3.Session(
                aws_access_key_id=self.conf('s3-access-key'),
                aws_secret_access_key=self.conf('s3-secret-key'))
        s3 = session.resource('s3', region_name=self.conf('s3-region'))

        s3.Bucket(self.conf('s3-bucket')).put_object(Key=self._get_key(achall),
                                                     Body=validation,
                                                     ACL='public-read')

        if response.simple_verify(
                achall.chall, achall.domain,
                achall.account_key.public_key(), self.config.http01_port):
            return response
        else:
            logger.error(
                "Self-verify of challenge failed, authorization abandoned!")
            return None

    def cleanup(self, achalls):
        # pylint: disable=missing-docstring,no-self-use,unused-argument
        session = boto3.Session(
                aws_access_key_id=self.conf('s3-access-key'),
                aws_secret_access_key=self.conf('s3-secret-key'))
        s3 = session.resource('s3', region_name=self.conf('s3-region'))
        client = s3.meta.client
        for achall in achalls:
            client.delete_object(Bucket=self.conf('s3-bucket'),
                                 Key=self._get_key(achall))
        return None
