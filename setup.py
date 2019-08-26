from setuptools import setup

setup(
    name='invoicer',
    packages=['invoicer'],
    include_package_data=True,
    install_requires=[
        'argon2-cffi',
        'arrow',
        'Flask-Caching',
        'Flask-Login',
        'Flask-Migrate',
        'Flask-QRcode',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'flask>=1.0.0',
        'htmlmin',
        'pdfkit',
        'premailer',
        'pyotp',
        'ruamel.yaml',
        'SQLAlchemy-Utils',
        'uwsgi;platform_system=="Linux"'
    ],
    extras_require={
        'test': ['pytest-flask', 'flake8'],
        'manage': ['Fabric'],
        'memcached': ['python-memcached']
    },
)
