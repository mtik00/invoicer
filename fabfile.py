#!/usr/bin/env python
"""
This script is used to control deployment of the invoicer app
"""
# Imports ######################################################################
import os
from fabric.utils import abort
from fabric.api import env, task
from fabric.operations import run, sudo, local
from fabric.context_managers import cd, prefix


# Metadata ####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "02-APR-2018"
__license__ = "MIT"

# Globals #####################################################################
INVOICER_APP_HOME_FOLDER = os.environ['INVOICER_APP_HOME_FOLDER']
VENV_DIR = os.environ['INVOICER_VENV_DIR'].strip('"').strip("'")
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
        sudo('PATH=' + VENV_DIR + ':$PATH bash deploy.bash')
