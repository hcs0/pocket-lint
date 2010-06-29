from distutils.core import setup

setup(
    name="pocketlint",
    description="Pocket-lint a composite linter and style checker.",
    version="0.1.0",
    maintainer="Curtis C. Hovey",
    maintainer_email="sinzui.is@verizon.net",
    url="https://launchpad.net/pocket-lint",
    packages=[
        'pocketlint', 'pocketlint/contrib', 'pocketlint/contrib/pyflakes'],
    scripts=['scripts/pocketlint'],
    )
