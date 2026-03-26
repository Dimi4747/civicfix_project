"""
WSGI config for CivicFix project - Passenger Deployment
Configuration pour nyem.cdwfs.net
"""

import os
import sys

# Chemin vers l'interpréteur Python de l'environnement virtuel
INTERP = os.path.expanduser("~/nyem/venv/bin/python3")
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Ajouter le chemin du projet au Python path
sys.path.insert(0, os.path.expanduser('~/nyem'))

# Définir le module de settings Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Importer l'application WSGI Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
