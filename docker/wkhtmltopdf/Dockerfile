# Ripped from https://github.com/lucenarenato/docker-alpine-wkhtmltopdf/blob/master/Dockerfile
# and added the service from https://github.com/openlabs/docker-wkhtmltopdf-aas/blob/master/app.py

FROM python:3.8-alpine3.12
LABEL maintainer="Timothy McFadden <tim@timandjamie.com>"

RUN apk add --update --no-cache \
    libgcc libstdc++ libx11 glib libxrender libxext libintl \
    ttf-dejavu ttf-droid ttf-freefont ttf-liberation ttf-ubuntu-font-family

# binary is static compiled against libssl1.0 libcrypto1.0 see issue #3
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.8/main' >> \
    /etc/apk/repositories && \
    apk --update --no-cache add libssl1.0 libcrypto1.0

RUN pip install werkzeug executor gunicorn

ADD app.py /app.py

ENTRYPOINT ["usr/local/bin/gunicorn"]

CMD ["-b", "0.0.0.0:80", "--log-file", "-", "app:application"]
