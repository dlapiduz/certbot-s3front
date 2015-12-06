"""S3/CloudFront Let's Encrypt installer plugin."""
import os
import logging
import re
import subprocess

import zope.component
import zope.interface

import boto3
import botocore

from acme import challenges

from letsencrypt import errors
from letsencrypt import interfaces
from letsencrypt.plugins import common


logger = logging.getLogger(__name__)

class Installer(common.Plugin):
    zope.interface.implements(interfaces.IInstaller)
    zope.interface.classProvides(interfaces.IPluginFactory)

    description = "S3/CloudFront Installer"

    @classmethod
    def add_parser_arguments(cls, add):
        add("cf-distribution-id", default=os.getenv('CF_DISTRIBUTION_ID'),
            help="CloudFront distribution id")

    def __init__(self, *args, **kwargs):
        super(Installer, self).__init__(*args, **kwargs)


    def prepare(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return ("")

    def get_all_names(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):
        """
        Upload Certificate to IAM and assign it to the CloudFront distribution
        """

        client = boto3.client('iam')
        cf_client = boto3.client('cloudfront')

        name = "le-%s" % domain
        body = open(cert_path).read()
        key = open(key_path).read()
        chain = open(chain_path).read()
        # Uplaod cert to IAM
        response = client.upload_server_certificate(
            Path="/cloudfront/letsencrypt/",
            ServerCertificateName=name + '-new',
            CertificateBody=body,
            PrivateKey=key,
            CertificateChain=chain
        )
        cert_id = response['ServerCertificateMetadata']['ServerCertificateId']
        # Update CloudFront config to use the new one
        cf_cfg = cf_client.get_distribution_config(Id=self.conf('cf-distribution-id'))
        cf_cfg['DistributionConfig']['ViewerCertificate']['IAMCertificateId'] = cert_id
        response = cf_client.update_distribution(DistributionConfig=cf_cfg['DistributionConfig'],
                                                 Id=self.conf('cf-distribution-id'),
                                                 IfMatch=cf_cfg['ETag'])

        # Delete old cert
        try:
            client.delete_server_certificate(
                ServerCertificateName=name
            )
        except botocore.exceptions.ClientError as e:
            logger.error(e)

        # Rename cert to the new one
        client.update_server_certificate(
            ServerCertificateName=name + '-new',
            NewServerCertificateName=name
        )

    def enhance(self, domain, enhancement, options=None):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def supported_enhancements(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def get_all_certs_keys(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def save(self, title=None, temporary=False):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def rollback_checkpoints(self, rollback=1):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def recovery_routine(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def view_config_changes(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def config_test(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def restart(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover
