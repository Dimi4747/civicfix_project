# Étape 1 : Build de l'image (multi-stage)
FROM python:3.11-slim AS builder

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Création du dossier de l'application
WORKDIR /app

# Copie des fichiers de dépendances
COPY requirements.txt ./

# Installation des dépendances Python dans un dossier isolé
RUN pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt

# Étape 2 : Image finale minimale
FROM python:3.11-slim

# Création d'un utilisateur non-root
RUN useradd --create-home appuser

WORKDIR /app

# Copie des dépendances installées depuis l'étape builder
COPY --from=builder /install /usr/local

# Copie du code source de l'application
COPY . /app

# Permissions pour l'utilisateur non-root
RUN chown -R appuser:appuser /app

# Passage à l'utilisateur non-root
USER appuser

# Port par défaut (à adapter selon l'app)
EXPOSE 8000

# Commande de démarrage (à adapter selon le serveur utilisé)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
