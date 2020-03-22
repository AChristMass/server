"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import get_default_application
import sys

from robotmissions import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "robotmissions.settings")

if settings.APPS_DIR not in sys.path:
    sys.path.append(settings.APPS_DIR)

django.setup()
application = get_default_application()
