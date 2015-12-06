import sys

from distutils.core import setup
from setuptools import find_packages

version = '0.1.0'

install_requires = [
    'acme>={0}'.format(version),
    'letsencrypt>={0}'.format(version),
    'PyOpenSSL',
    'pyparsing>=1.5.5',  # Python3 support; perhaps unnecessary?
    'setuptools',  # pkg_resources
    'zope.interface',
    'boto3'
]

if sys.version_info < (2, 7):
    install_requires.append('mock<1.1.0')
else:
    install_requires.append('mock')

docs_extras = [
    'Sphinx>=1.0',  # autodoc_member_order = 'bysource', autodoc_default_flags
    'sphinx_rtd_theme',
]

setup(
    name='letsencrypt-s3front',
    version=version,
    description="S3/CloudFront plugin for Let's Encrypt client",
    url='https://github.com/dlapiduz/letsencrypt-s3front',
    author="Diego Lapiduz",
    author_email='diego@lapiduz.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    keywords = ['letsencrypt', 'cloudfront', 's3'],
    entry_points={
        'letsencrypt.plugins': [
            'auth = letsencrypt_s3front.authenticator:Authenticator',
            'installer = letsencrypt_s3front.installer:Installer',
        ],
    },
)
