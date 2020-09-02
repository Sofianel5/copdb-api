"""
WSGI config for copdb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.append('/home/bitnami/apps/django/django_projects/copdb-api/copdb')
sys.path.append('/home/bitnami/apps/django/django_projects/copdb-api/copdb/copdb')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'copdb.settings')

application = get_wsgi_application()

