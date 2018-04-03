#!/usr/bin/env bash
# NOTE: This should be run in an already-activate virtual environment

# Make sure we bring in any changes to python #################################
pip install -r rquirements.txt
###############################################################################

# build the config files
flask build

# bootstrap the built deploy file
bash _build/deploy.bash
