#!/usr/bin/python

import subprocess

from distutils.core import (
    Command,
    setup,
    )
from distutils.command.sdist import sdist


class SignedSDistCommand(sdist):
    """Sign the source archive with a detached signature."""

    description = "Sign the source archive after it is generated."

    def run(self):
        sdist.run(self)
        gpg_args = [
            'gpg', '--armor', '--sign', '--detach-sig', self.archive_files[0]]
        gpg = subprocess.Popen(
            gpg_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        gpg.communicate()


class Check(Command):
    description = "Run unit tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_command_name(self):
        pass

    def run(self):
        test_args = ['./test.py']
        test = subprocess.Popen(
            test_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, errput = test.communicate()
        print errput


setup(
    name="pocketlint",
    description="Pocket-lint a composite linter and style checker.",
    version="0.5.32",
    maintainer="Curtis C. Hovey",
    maintainer_email="sinzui.is@verizon.net",
    url="https://launchpad.net/pocket-lint",
    packages=[
        'pocketlint', 'pocketlint/contrib'],
    package_dir={
        'pocketlint': 'pocketlint',
        'pocketlint/contrib': 'pocketlint/contrib'},
    package_data={
        'pocketlint': ['jsreporter.js'],
        'pocketlint/contrib': ['fulljslint.js'],
        },
    requires=['pyflakes (>=0.6)'],
    scripts=['scripts/pocketlint'],
    cmdclass={
        'check': Check,
        'signed_sdist': SignedSDistCommand,
        },
    )
