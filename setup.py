from setuptools import setup, find_packages

from ghostpass import consts

# Important constants
NAME = consts.NAME
VERSION = consts.VERSION
REPO = "https://github.com/ex0dus-0x/ghostpass"
DESC = """Ghostpass is a dead simple password management system that enables
users to distribute cleartext-like ciphertext to the open web, while still
maintaining security and data integrity."""

# Main setup method
setup(
    name = NAME,
    version = VERSION,
    author = "Alan Cao",
    author_email = 'ex0dus@codemuch.tech',
    description = DESC,
    license = "GPLv3",
    url=REPO,
    download_url='{}/archive/v{}'.format(REPO, VERSION),
    keywords=[
        'passwords',
        'cryptography',
        'systems',
        'secret-sharing',
        'privacy',
    ],
    packages = find_packages(exclude=('tests',)),
    entry_points = {
        'console_scripts': [
            'ghostpass=ghostpass.__main__:main'
        ],
    },
    install_requires=[
        'names',
        'pycrypto',
        'jsonpickle',
        'tabulate',
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
    ]
)
