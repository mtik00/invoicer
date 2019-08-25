#!/usr/bin/env bash
# NOTE: This should be run in an already-activate virtual environment on the
# target host.

# Make sure we bring in any changes to python #################################
pip install -e .
###############################################################################

# make sure the build directory is clear
rm -rf _build/*

# build the config files
flask build

# Back up the database
if [[ -e instance/invoicer.db ]]; then
    cp -f instance/invoicer.db instance/invoicer-$(date +%F_%R:%S).db
fi

# Upgrade the database
flask db upgrade

# bootstrap the built deploy file
sudo bash _build/deploy.bash
