#!/usr/bin/env bash

export WORKON_HOME=/var/envs
export PROJECT_HOME=/var/www/subdomains/codebnb
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export VIRTUALENVWRAPPER_HOOK_DIR=/var/envs/bin
export PIP_RESPECT_VIRTUALENV=true

source /var/envs/calorie/bin/activate

cd /var/www/subdomains/codebnb/calorie/

python manage.py init_default_consumer
