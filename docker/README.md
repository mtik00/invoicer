# Invoicer Docker

This app was meant to be deployed in containers.

## web

The flask app is hosted in the `web` container.  This container is base on `slim-buster` due to the requirements of things like `argon2` and `locale`.  Otherise I'd probably just use `3.8-alpine`.

## wkhtmltopdf

This is a custom-built image combined from two separate projects:

* https://github.com/lucenarenato/docker-alpine-wkhtmltopdf
* https://github.com/openlabs/docker-wkhtmltopdf-aas

...with some changes to make everything work.

This is an alpine-based image that accepts requests and returns a PDF.  I'm using a separate image because I want to keep the images as small as possible.  It's just too hard to put everything into a single image without it growing to over 1GB.

# docker-compose

There's a `docker-compose.yml` file that you can use to bring up/down the containers.  It should work just fine!

The only hitch is the _instance_ folder.  The idea is that you'd put this folder along side the compose file.  This will store things like the `application.cfg` file, the database, etc.
