"""
WSGI config for invoice_app project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""
import os, sys
from django.core.wsgi import get_wsgi_application

print("=== RUNTIME DEBUG ===")
print("Python version:", sys.version)
print("Sys path:", sys.path)
print("DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"))
print("=====================")

application = get_wsgi_application()
app = get_wsgi_application()