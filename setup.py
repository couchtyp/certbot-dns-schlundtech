from setuptools import setup
from setuptools import find_packages


version = '0.5.0'

# Remember to update local-oldest-requirements.txt when changing the minimum
# acme/certbot version.
install_requires = [
    'acme>=0.29.0',
    'certbot>=1.0.0',
    'mock',
    'setuptools',
    'zope.interface',
    'pyotp',
]

docs_extras = [
]

setup(
    name='certbot-dns-schlundtech',
    version=version,
    description="SchlundTech XML Gateway DNS Authenticator plugin for Certbot",
    url='https://github.com/couchtyp/certbot-dns-schlundtech',
    author="Philipp Mueller",
    author_email='pmueller@maildir.eu',
    license='MIT License',
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
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
    extras_require={
        'docs': docs_extras,
    },
    entry_points={
        'certbot.plugins': [
            'dns-schlundtech = certbot_dns_schlundtech.dns_schlundtech:Authenticator',
            # backward compatability:
            'certbot-dns-schlundtech:auth = certbot_dns_schlundtech.dns_schlundtech:Authenticator',
        ],
    },
    test_suite='certbot_dns_schlundtech',
)
