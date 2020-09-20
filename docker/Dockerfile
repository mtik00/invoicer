FROM python:3.8-buster as builder

# Build our app inside a virtual environment so we can copy
# it out later.

RUN python -m venv --copies  /tmp/app-env

WORKDIR /tmp/app-builder

COPY ./requirements.txt ./setup.py MANIFEST.in ./
COPY ./invoicer ./invoicer

RUN /tmp/app-env/bin/python -m pip install --upgrade pip && \
    /tmp/app-env/bin/python -m pip install -r requirements.txt && \
    /tmp/app-env/bin/python -m pip install . && \
    find . -name "*.py[co]" -o -name __pycache__ -exec rm -rf {} +

# Make the virtual env portable
RUN sed -i '40s/.*/VIRTUAL_ENV="$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}" )")" \&\& pwd)"/' /tmp/app-env/bin/activate
RUN sed -i '1s|.*|#!/usr/bin/env python|' /tmp/app-env/bin/pip*
RUN sed -i '1s/.*python$/#!\/usr\/bin\/env python/' /tmp/app-env/bin/*

# Stuff to help debug
# RUN apt-get update && apt-get install -y vim wget curl && \
#     echo "alias ll='ls -alh'" >> /root/.bashrc

#################################################################################
# All we need to do is to set up the container and copy the pre-built virtual env
FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/src/app/.venv/bin:$PATH"

LABEL maintainer="tim@timandjamie.com"
LABEL app="invoicer"

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y locales libxml2 tini dnsutils  \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash webapp-user \
    && echo "alias ll='ls -alh'" >> /home/webapp-user/.bashrc \
    && echo 'PATH="/usr/src/app/.venv/bin:$PATH"' >> /home/webapp-user/.bashrc \
    && mkdir /var/log/invoicer && chown webapp-user:webapp-user /var/log/invoicer

WORKDIR /usr/src/app

COPY ./wsgi.py docker/uwsgi.ini ./

COPY --from=builder /tmp/app-env /usr/src/app/.venv

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "uwsgi", "--ini", "uwsgi.ini" ]

RUN chown webapp-user:webapp-user /usr/src/app

USER webapp-user
