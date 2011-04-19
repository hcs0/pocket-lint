import subprocess

from distutils.core import setup
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

setup(
    name="pocketlint",
    description="Pocket-lint a composite linter and style checker.",
    version="0.5.15",
    maintainer="Curtis C. Hovey",
    maintainer_email="sinzui.is@verizon.net",
    url="https://launchpad.net/pocket-lint",
    packages=[
        'pocketlint', 'pocketlint/contrib', 'pocketlint/contrib/pyflakes'],
    package_dir={
        'pocketlint': 'pocketlint',
        'pocketlint/contrib': 'pocketlint/contrib'},
    package_data={
        'pocketlint': ['jsreporter.js'],
        'pocketlint/contrib': ['fulljslint.js'],
        },
    scripts=['scripts/pocketlint'],
    cmdclass={
        'signed_sdist': SignedSDistCommand,
        },
    )
