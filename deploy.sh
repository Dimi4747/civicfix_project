#!/bin/bash

# Script de déploiement automatique pour CivicFix
# Usage: ./deploy.sh

echo "🚀 Démarrage du déploiement de CivicFix..."

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Vérifier si on est dans le bon répertoire
if [ ! -f "manage.py" ]; then
    print_error "Erreur: manage.py introuvable. Êtes-vous dans le bon répertoire?"
    exit 1
fi

# Activer l'environnement virtuel
print_info "Activation de l'environnement virtuel..."
if [ -d "venv" ]; then
    source venv/bin/activate
    print_success "Environnement virtuel activé"
elif [ -d "env" ]; then
    source env/bin/activate
    print_success "Environnement virtuel activé"
else
    print_error "Environnement virtuel introuvable"
    exit 1
fi

# Mettre à jour le code depuis Git (optionnel)
read -p "Voulez-vous mettre à jour depuis Git? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Mise à jour depuis Git..."
    git pull origin main
    print_success "Code mis à jour"
fi

# Installer/Mettre à jour les dépendances
print_info "Installation des dépendances..."
pip install -r requirements.txt --quiet
print_success "Dépendances installées"

# Appliquer les migrations
print_info "Application des migrations..."
python manage.py migrate --noinput
print_success "Migrations appliquées"

# Collecter les fichiers statiques
print_info "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --clear
print_success "Fichiers statiques collectés"

# Créer le dossier logs s'il n'existe pas
if [ ! -d "logs" ]; then
    mkdir logs
    print_success "Dossier logs créé"
fi

# Créer le dossier tmp pour Passenger s'il n'existe pas
if [ ! -d "tmp" ]; then
    mkdir tmp
    print_success "Dossier tmp créé"
fi

# Vérifier la configuration
print_info "Vérification de la configuration..."
python manage.py check --deploy
if [ $? -eq 0 ]; then
    print_success "Configuration valide"
else
    print_error "Erreurs de configuration détectées"
    exit 1
fi

# Redémarrer l'application Passenger
print_info "Redémarrage de l'application..."
touch tmp/restart.txt
print_success "Application redémarrée"

echo ""
print_success "🎉 Déploiement terminé avec succès!"
echo ""
print_info "Prochaines étapes:"
echo "  1. Vérifiez votre site: https://votre-domaine.com"
echo "  2. Consultez les logs: tail -f logs/django.log"
echo "  3. Testez l'admin: https://votre-domaine.com/admin/"
echo ""
