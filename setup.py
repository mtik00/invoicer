from setuptools import setup, find_packages

setup(
    name='invoicer',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['templates/*.html'] }
)
