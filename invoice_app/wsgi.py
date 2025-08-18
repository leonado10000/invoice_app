import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "invoice_app.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = get_wsgi_application()