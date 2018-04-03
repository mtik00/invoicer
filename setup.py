from setuptools import setup

setup(
    name='invoicer',
    packages=['invoicer'],
    include_package_data=True,
    install_requires=[
        'argon2-cffi==18.1.0',
        'arrow==0.12.0',
        'Flask-Caching==1.3.3',
        'Flask-Login==0.4.1',
        'Flask-Migrate==2.1.1',
        'Flask-SQLAlchemy==2.3.2',
        'Flask-WTF==0.14.2',
        'Flask==0.12.2',
        'htmlmin==0.1.12',
        'pdfkit==0.6.1',
        'premailer==3.1.1',
        'ruamel.yaml==0.15.37',
        'SQLAlchemy-Utils==0.32.21',
        'uwsgi==2.0.17;platform_system=="Linux"'
    ],
    extras_require={
        'test': ['pytest-flask==0.10.0', 'flake8'],
        'manage': ['Fabric==1.14.0']
    },
)
