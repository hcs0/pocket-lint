from distutils.core import setup

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
    )
