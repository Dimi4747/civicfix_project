"""
WSGI config for CivicFix project - Passenger Deployment
This file is used by Passenger to serve the Django application
"""

import os
import sys

# Ajouter le répertoire du projet au path Python
INTERP = os.path.expanduser("~/virtualenv/civicfix_project/3.11/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(__file__))

# Définir le module de settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Importer l'application WSGI Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
