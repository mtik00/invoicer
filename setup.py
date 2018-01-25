from setuptools import setup

setup(
    name='invoicer',
    packages=['invoicer'],
    include_package_data=True,
    install_requires=[
        'argon2-cffi==18.1.0',
        'arrow==0.12.0',
        'Flask-WTF==0.14.2',
        'Flask==0.12.2',
        'pdfkit==0.6.1',
        'premailer==3.1.1',
        'Flask-SQLAlchemy==2.3.2',
        'SQLAlchemy-Utils==0.32.21'
    ],
)