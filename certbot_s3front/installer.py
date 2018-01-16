"""S3/CloudFront Let's Encrypt installer plugin."""

from __future__ import print_function

import os
import os.path
import sys
import logging

import zope.interface

import boto3
import botocore

from certbot import interfaces
from certbot.plugins import common


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
        return ""

    def get_all_names(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):
        """
        Upload Certificate to IAM and assign it to the CloudFront distribution
        """
        if self.config.rsa_key_size > 2048:
            print(
                "The maximum public key size allowed for Cloudfront is 2048 ("
                "https://docs.aws.amazon.com/AmazonCloudFront/latest"
                "/DeveloperGuide/cnames-and-https-requirements.html)\n"
                "Please, use --rsa_key_size 2048 or edit your cli.ini")
            sys.exit(1)
        client = boto3.client('iam')
        cf_client = boto3.client('cloudfront')

        name = "le-%s" % domain
        body = open(cert_path).read()
        key = open(key_path).read()
        chain = open(chain_path).read()

        suffix = "-%i" % int(os.path.getmtime(cert_path))

        # Check if certificate already exists
        certificates = client.list_server_certificates(
            PathPrefix="/cloudfront/letsencrypt/"
        )
        cert_id = None
        for cert in certificates['ServerCertificateMetadataList']:
            if cert['ServerCertificateName'] == (name + suffix):
                cert_id = cert['ServerCertificateId']

        # If certificate doesn't already exists, upload cert to IAM
        if not cert_id:
            response = client.upload_server_certificate(
                Path="/cloudfront/letsencrypt/",
                ServerCertificateName=name + suffix,
                CertificateBody=body,
                PrivateKey=key,
                CertificateChain=chain
            )
            cert_id = response['ServerCertificateMetadata']['ServerCertificateId']

        # Update CloudFront config to use the new one
        cf_cfg = cf_client.get_distribution_config(Id=self.conf('cf-distribution-id'))
        cf_cfg['DistributionConfig']['ViewerCertificate']['IAMCertificateId'] = cert_id
        cf_cfg['DistributionConfig']['ViewerCertificate']['Certificate'] = cert_id
        cf_cfg['DistributionConfig']['ViewerCertificate']['CertificateSource'] = 'iam'

        # Set the default mode to SNI-only to avoid surprise charges
        if 'SSLSupportMethod' not in cf_cfg['DistributionConfig']['ViewerCertificate']:
            cf_cfg['DistributionConfig']['ViewerCertificate']['SSLSupportMethod'] = 'sni-only'
            cf_cfg['DistributionConfig']['ViewerCertificate']['MinimumProtocolVersion'] = 'TLSv1'

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

        # Delete old certs
        certificates = client.list_server_certificates(
            PathPrefix="/cloudfront/letsencrypt/"
        )
        for cert in certificates['ServerCertificateMetadataList']:
            if (cert['ServerCertificateName'].startswith(name) and
                    cert['ServerCertificateName'] != name + suffix):
                try:
                    client.delete_server_certificate(
                        ServerCertificateName=cert['ServerCertificateName']
                    )
                except botocore.exceptions.ClientError as e:
                    logger.error(e)

    def enhance(self, domain, enhancement, options=None):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def supported_enhancements(self):  # pylint: disable=missing-docstring,no-self-use
        return []  # pragma: no cover

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

    def _get_domain_from_certificate_name(self, cert_name):
        """Parse ServerCertificateName from IAM.

        Certificate Names usually take the form of "le-example.com" or
        "le-example.com-1234567890". We want to extract the actual domain
        name to ensure we're uploading and deleting the correct certificates.
        """
        # Remove Let's Encrypt prefix
        cert_name = cert_name.lstrip('le-')

        # Remove trailing numbers if present (as last 10 characters)
        name_fragments = cert_name.split('-')
        if len(name_fragments) > 1 and name_fragments[-1].isdigit():
            name_fragments = name_fragments[:-1]
        return '-'.join(name_fragments)

    def restart(self):
        client = boto3.client('iam')
        certificates = client.list_server_certificates(
            PathPrefix="/cloudfront/letsencrypt/"
        )

        for domain in self.config.domains:
            for cert in certificates['ServerCertificateMetadataList']:
                cert_name = cert['ServerCertificateName']
                if domain == self._get_domain_from_certificate_name(cert_name):
                    cert_path = os.path.join(self.config.live_dir, domain, 'cert.pem')
                    chain_path = os.path.join(self.config.live_dir, domain, 'chain.pem')
                    fullchain_path = os.path.join(self.config.live_dir, domain, 'fullchain.pem')
                    key_path = os.path.join(self.config.live_dir, domain, 'privkey.pem')
                    try:
                        open(cert_path, 'r')
                    except IOError as e:
                        logger.error(e)
                        continue
                    self.deploy_cert(domain, cert_path, key_path, chain_path, fullchain_path)
