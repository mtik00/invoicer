#!/usr/bin/env python2.7
"""
This script is used to control deployment of the invoicer app
"""
# Imports ######################################################################
import os
import json
import zlib
from fabric.utils import abort
from fabric.api import env, task
from fabric.operations import run, sudo, local
from fabric.context_managers import cd


# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "02-APR-2018"
__license__ = "MIT"

# Globals #####################################################################
INVOICER_APP_HOME_FOLDER = os.environ['INVOICER_APP_HOME_FOLDER']
VENV_ACTIVATE = os.environ.get('INVOICER_VENV_ACTIVATE_COMMAND')
###############################################################################

# Fabric environment setup ####################################################
env.hosts = os.environ['INVOICER_APP_HOST']
env.colorize_errors = True
env.use_ssh_config = True
env.password = os.environ.get('INVOICER_APP_SUDO_PASSWORD')
###############################################################################


@task
def deploy():
    """
    Deploy the application
    """
    # Don't deploy if we aren't clean!
    if local('git status --porcelain', capture=True):
        abort("Can't deploy unless we are clean!")

    with cd(INVOICER_APP_HOME_FOLDER):
        run('git reset --hard HEAD')
        run('git pull')

        with prefix(VENV_ACTIVATE):
            sudo('bash deploy.bash')
