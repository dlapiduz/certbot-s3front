"""S3/CloudFront Let's Encrypt installer plugin."""

from __future__ import print_function

import os
import sys
import logging
import time

import zope.interface

import boto3
import botocore

from certbot import interfaces
from certbot.plugins import common


logger = logging.getLogger(__name__)


@zope.interface.implementer(interfaces.IInstaller)
@zope.interface.provider(interfaces.IPluginFactory)
class Installer(common.Installer):
    description = "S3/CloudFront Installer"

    @classmethod
    def add_parser_arguments(cls, add):
        add("cf-distribution-id", default=os.getenv('CF_DISTRIBUTION_ID'),
            help="CloudFront distribution id")

    def __init__(self, *args, **kwargs):
        self.certificate_main_domain = None
        self.certificate_id = None
        super(Installer, self).__init__(*args, **kwargs)


    def prepare(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return ""

    def get_all_names(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):
        """
        Upload Certificate to IAM
        """

        # Only install a certificate once
        if self.certificate_id is not None:
            return

        if self.config.rsa_key_size > 2048:
            logger.error(
                "The maximum public key size allowed for Cloudfront is 2048 ("
                "https://docs.aws.amazon.com/AmazonCloudFront/latest"
                "/DeveloperGuide/cnames-and-https-requirements.html)\n"
                "Please, use --rsa_key_size 2048 or edit your cli.ini")
            sys.exit(1)
        client = boto3.client('iam')

        name = "le-%s" % domain
        body = open(cert_path).read()
        key = open(key_path).read()
        chain = open(chain_path).read()

        suffix = "-%i" % int(time.time())

        # Upload cert to IAM
        response = client.upload_server_certificate(
            Path="/cloudfront/letsencrypt/",
            ServerCertificateName=name + suffix,
            CertificateBody=body,
            PrivateKey=key,
            CertificateChain=chain
        )

        self.certificate_id = response['ServerCertificateMetadata']['ServerCertificateId']
        self.certificate_main_domain = domain

    def enhance(self, domain, enhancement, options=None):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def supported_enhancements(self):  # pylint: disable=missing-docstring,no-self-use
        return []  # pragma: no cover

    def get_all_certs_keys(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def save(self, title=None, temporary=False):  # pylint: disable=no-self-use
        """
        Save the Cloudfront config if needed
        """

        if self.certificate_id is None:
            # Nothing to save
            return

        client = boto3.client('iam')
        cf_client = boto3.client('cloudfront')

        # Update CloudFront config to use the new one
        cf_cfg = cf_client.get_distribution_config(Id=self.conf('cf-distribution-id'))

        # If we already have the right certificate, then don't change the config.
        if ('IAMCertificateId' in cf_cfg['DistributionConfig']['ViewerCertificate'] and
                cf_cfg['DistributionConfig']['ViewerCertificate']['IAMCertificateId'] == self.certificate_id):
            return

        cf_cfg['DistributionConfig']['ViewerCertificate']['IAMCertificateId'] = self.certificate_id
        cf_cfg['DistributionConfig']['ViewerCertificate']['Certificate'] = self.certificate_id
        cf_cfg['DistributionConfig']['ViewerCertificate']['CertificateSource'] = 'iam'

        # Set the default mode to SNI-only to avoid surprise charges
        if 'SSLSupportMethod' not in cf_cfg['DistributionConfig']['ViewerCertificate']:
            cf_cfg['DistributionConfig']['ViewerCertificate']['SSLSupportMethod'] = 'sni-only'
            cf_cfg['DistributionConfig']['ViewerCertificate']['MinimumProtocolVersion'] = 'TLSv1.2_2018'

        try:
            cf_cfg['DistributionConfig']['ViewerCertificate'].pop('CloudFrontDefaultCertificate')
        except KeyError:
            pass
        try:
            cf_cfg['DistributionConfig']['ViewerCertificate'].pop('ACMCertificateArn')
        except KeyError:
            pass
        response = cf_client.update_distribution(DistributionConfig=cf_cfg['DistributionConfig'],
                                                 Id=self.conf('cf-distribution-id'),
                                                 IfMatch=cf_cfg['ETag'])
        # TODO check response

        # Delete old certs
        certificates = client.list_server_certificates(
            PathPrefix="/cloudfront/letsencrypt/"
        )
        for cert in certificates['ServerCertificateMetadataList']:
            if (self.certificate_main_domain in cert['ServerCertificateName'] and
                    cert['ServerCertificateId'] != self.certificate_id):
                try:
                    client.delete_server_certificate(
                        ServerCertificateName=cert['ServerCertificateName']
                    )
                except botocore.exceptions.ClientError as e:
                    logger.error(e)


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

    def renew_deploy(self, lineage, *args, **kwargs): # pylint: disable=missing-docstring,no-self-use
        """
        Renew certificates when calling `certbot renew`
        """

        # Run deploy_cert with the lineage params
        self.deploy_cert(lineage.names()[0], lineage.cert_path, lineage.key_path, lineage.chain_path, lineage.fullchain_path)

        return

interfaces.RenewDeployer.register(Installer)
