# Ripped from https://github.com/lucenarenato/docker-alpine-wkhtmltopdf/blob/master/Dockerfile
# and added the service from https://github.com/openlabs/docker-wkhtmltopdf-aas/blob/master/app.py

FROM python:rc-alpine3.12
LABEL maintainer="Timothy McFadden <tim@timandjamie.com>"

RUN apk add --update --no-cache \
    libgcc libstdc++ libx11 glib libxrender libxext libintl \
    ttf-dejavu ttf-droid ttf-freefont ttf-liberation ttf-ubuntu-font-family

# binary is static compiled against libssl1.0 libcrypto1.0 see issue #3
RUN echo 'http://dl-cdn.alpinelinux.org/alpine/v3.8/main' >> \
    /etc/apk/repositories && \
    apk --update --no-cache add libssl1.0 libcrypto1.0

# on alpine static compiled patched qt headless wkhtmltopdf (47.2 MB)
# compilation takes 4 hours on EC2 m1.large in 2016 thats why binary
RUN wget -O /bin/wkhtmltopdf https://github.com/lucenarenato/docker-alpine-wkhtmltopdf/raw/master/wkhtmltopdf \
    && chmod +x /bin/wkhtmltopdf

RUN pip install werkzeug gunicorn

ADD app.py /app.py

ENTRYPOINT ["usr/local/bin/gunicorn"]

CMD ["-b", "0.0.0.0:80", "--log-file", "-", "app:application"]
