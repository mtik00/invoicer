from setuptools import setup

setup(
    name='invoicer',
    packages=['invoicer'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)