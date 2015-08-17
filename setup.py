# Copyright 2013-2014 Synappio LLC. All rights reserved.
import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.md')).read()

setup(
    name='synappio-client',
    version='0.0',
    description='Synapp.io API Clients',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
    ],
    author='',
    author_email='',
    url='',
    keywords='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    tests_require=[],
    test_suite="synappio-client",
    entry_points="""\
    [paste.app_factory]
    doc = seas.doc:DocServer.factory

    [paste.filter_factory]

    [paste.server_factory]

    [console_scripts]
    mdp-broker = seas.zutil.mdp.script:run_mdp_broker

    """,
)
