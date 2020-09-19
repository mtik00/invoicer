FROM python:3.8-buster as builder

# Build our app inside a virtual environment so we can copy
# it out later.
RUN apt-get upgrade && apt-get update -y \
    && apt-get install -y python-virtualenv wget

RUN virtualenv --python=python3 --always-copy /tmp/app-env

# Make the virtual env portable
RUN sed -i '43s/.*/VIRTUAL_ENV="$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}" )")" \&\& pwd)"/' /tmp/app-env/bin/activate \
    && sed -i '1s/.*/#!\/usr\/bin\/env python/' /tmp/app-env/bin/pip*

ENV PATH="/tmp/app-env/bin:$PATH"

WORKDIR /tmp/app-builder

COPY ./requirements.txt .
COPY ./setup.py .
COPY ./invoicer ./invoicer

RUN /tmp/app-env/bin/python -m pip install --no-cache-dir -r requirements.txt
RUN /tmp/app-env/bin/python -m pip install .

#################################################################################
# All we need to do is to set up the container and copy the pre-built virtual env
FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/src/app/.venv/bin:$PATH"

LABEL maintainer="tim@timandjamie.com"

RUN apt-get upgrade && apt-get update -y \
    && apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash webapp-user \
    && echo "alias ll='ls -alh'" >> /home/webapp-user/.bashrc \
    && echo 'PATH="/usr/src/app/.venv/bin:$PATH"' >> /home/webapp-user/.bashrc \
    && mkdir /var/log/invoicer && chown webapp-user:webapp-user /var/log/invoicer

USER webapp-user
WORKDIR /usr/src/app
COPY --from=builder /tmp/app-env /usr/src/app/.venv
