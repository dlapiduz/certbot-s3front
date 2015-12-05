"""S3/CloudFront Let's Encrypt authenticator plugin."""
import os
import logging
import re
import subprocess

import zope.component
import zope.interface

import boto3

from acme import challenges

from letsencrypt import errors
from letsencrypt import interfaces
from letsencrypt.plugins import common


logger = logging.getLogger(__name__)

class Authenticator(common.Plugin):
    zope.interface.implements(interfaces.IAuthenticator)
    zope.interface.classProvides(interfaces.IPluginFactory)

    description = "S3/CloudFront Authenticator"

    @classmethod
    def add_parser_arguments(cls, add):
        add("s3-bucket", default=os.getenv('S3_BUCKET'),
            help="Bucket referenced by CloudFront distribution")

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

    def perform(self, achalls):  # pylint: disable=missing-docstring
        responses = []
        for achall in achalls:
            responses.append(self._perform_single(achall))
        return responses

    def _perform_single(self, achall):
        # upload the challenge file to the desired s3 bucket
        # then run simple http verification
        response, validation = achall.response_and_validation()
        s3 = boto3.resource('s3')

        s3.Bucket(self.conf('s3-bucket')).put_object(Key=achall.chall.path[1:],
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
        return None
