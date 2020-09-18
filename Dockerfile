FROM python:3.8-buster as builder

# Build our app inside a virtual environment so we can copy
# it out later.
RUN apt-get upgrade && apt-get update -y \
    && apt-get install -y python-virtualenv

RUN virtualenv --python=python3 /tmp/app-env

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

RUN useradd -ms /bin/bash webapp-user \
    && echo "alias ll='ls -alh'" >> /home/webapp-user/.bashrc \
    && echo 'PATH="/usr/src/app/.venv/bin:$PATH"' >> /home/webapp-user/.bashrc

USER webapp-user
WORKDIR /usr/src/app
COPY --from=builder /tmp/app-env /usr/src/app/.venv
