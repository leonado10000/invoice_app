import os, sys

print("=== RUNTIME DEBUG ===")
print("Python version:", sys.version)
print("Sys path:", sys.path)
print("DJANGO_SETTINGS_MODULE:", os.environ.get("DJANGO_SETTINGS_MODULE"))
print("=====================")

# 👇 Force Django to know where settings.py is
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "invoice_app.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
