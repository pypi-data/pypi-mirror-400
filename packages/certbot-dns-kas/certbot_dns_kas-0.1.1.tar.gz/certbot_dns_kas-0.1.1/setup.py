from setuptools import setup
from setuptools import find_packages

setup(
    name='certbot-dns-kas',
    version='0.1.1',
    description='All-Inkl KAS DNS Authenticator plugin for Certbot',
    url='https://github.com/mobilandi/certbot-dns-kas',
    author='Antigravity',
    author_email='antigravity@example.com',
    license='Apache License 2.0',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'certbot>=1.18.0',
        'zope.interface',
        'kasserver',
    ],
    entry_points={
        'certbot.plugins': [
            'dns-kas = certbot_dns_kas._internal.dns_kas:Authenticator',
        ],
    },
)
