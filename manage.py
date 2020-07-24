#!/usr/bin/env python
import os
import sys

import dotenv

if __name__ == '__main__':

    dotenv.read_dotenv()

    settings_file = 'production'
    if os.environ.get('IS_LOCAL') == 'True':
        settings_file = 'local'
    elif os.environ.get('IS_CODEBNB') == 'True':
        settings_file = 'codebnb'

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calorie.settings.' + settings_file)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
