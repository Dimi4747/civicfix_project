# Requirements Document

## Introduction

Ce document définit les exigences pour l'automatisation de l'analyse de sécurité avec SonarQube et du déploiement continu vers le serveur O2Switch pour le projet CivicFix. Le système doit analyser automatiquement chaque commit pour détecter les vulnérabilités, puis déployer automatiquement les versions validées sur l'environnement de production.

## Glossary

- **CI_Pipeline**: Le pipeline d'intégration continue GitHub Actions qui exécute les analyses et tests
- **SonarQube_Analyzer**: Le service SonarQube qui analyse le code pour détecter vulnérabilités, bugs et problèmes de qualité
- **CD_Pipeline**: Le pipeline de déploiement continu qui déploie automatiquement vers O2Switch
- **O2Switch_Server**: Le serveur de production hébergeant CivicFix (nyem.cdwfs.net)
- **Quality_Gate**: Le seuil de qualité défini dans SonarQube qui doit être respecté pour autoriser le déploiement
- **Deployment_Blocker**: Une vulnérabilité ou problème critique qui empêche le déploiement automatique
- **Notification_System**: Le système qui envoie des alertes à l'équipe en cas de problème
- **Deployment_Artifact**: L'ensemble des fichiers et configurations nécessaires au déploiement
- **Rollback_Mechanism**: Le mécanisme permettant de revenir à une version précédente en cas d'échec
- **Audit_Log**: Le journal traçant tous les déploiements et leurs résultats

## Requirements

### Requirement 1: Analyse Automatique avec SonarQube

**User Story:** En tant que développeur, je veux que chaque commit soit automatiquement analysé par SonarQube, afin de détecter les vulnérabilités de sécurité et problèmes de qualité dès leur introduction.

#### Acceptance Criteria

1. WHEN a commit is pushed to any branch, THE CI_Pipeline SHALL trigger a SonarQube_Analyzer scan within 60 seconds
2. THE SonarQube_Analyzer SHALL analyze Python code for security vulnerabilities, bugs, code smells, and code coverage
3. THE SonarQube_Analyzer SHALL report results including security hotspots, vulnerability severity levels, and technical debt
4. WHEN the analysis completes, THE CI_Pipeline SHALL display the SonarQube results in the GitHub Actions interface
5. THE SonarQube_Analyzer SHALL maintain historical analysis data for trend tracking across commits

### Requirement 2: Quality Gate Enforcement

**User Story:** En tant que responsable qualité, je veux bloquer les déploiements qui ne respectent pas les standards de qualité, afin de garantir la sécurité et la fiabilité du code en production.

#### Acceptance Criteria

1. THE CI_Pipeline SHALL evaluate the Quality_Gate status after each SonarQube_Analyzer scan
2. IF a critical or high severity vulnerability is detected, THEN THE CI_Pipeline SHALL mark the build as failed
3. IF the Quality_Gate fails, THEN THE CI_Pipeline SHALL prevent the CD_Pipeline from executing
4. WHEN the Quality_Gate fails, THE Notification_System SHALL send an alert to the development team within 2 minutes
5. THE Quality_Gate SHALL enforce thresholds for security vulnerabilities (0 critical, 0 high), code coverage (minimum 70%), and duplicated code (maximum 3%)

### Requirement 3: Déploiement Automatique vers O2Switch

**User Story:** En tant que développeur, je veux que les commits validés sur la branche main soient automatiquement déployés sur O2Switch, afin d'accélérer la mise en production et réduire les erreurs manuelles.

#### Acceptance Criteria

1. WHEN a commit is pushed to the main branch AND the Quality_Gate passes, THE CD_Pipeline SHALL initiate deployment to O2Switch_Server
2. THE CD_Pipeline SHALL connect to O2Switch_Server via SSH using encrypted credentials stored in GitHub Secrets
3. THE CD_Pipeline SHALL execute the deployment sequence: pull code, install dependencies, run migrations, collect static files, and restart Passenger
4. WHEN deployment starts, THE CD_Pipeline SHALL create a Deployment_Artifact containing commit hash, timestamp, and deployer identity
5. THE CD_Pipeline SHALL complete the full deployment process within 5 minutes

### Requirement 4: Gestion des Migrations de Base de Données

**User Story:** En tant qu'administrateur système, je veux que les migrations de base de données soient appliquées automatiquement et en toute sécurité, afin d'éviter les incohérences entre le code et le schéma de données.

#### Acceptance Criteria

1. WHEN deploying to O2Switch_Server, THE CD_Pipeline SHALL execute Django migrations before restarting the application
2. IF a migration fails, THEN THE CD_Pipeline SHALL halt deployment and preserve the previous application state
3. THE CD_Pipeline SHALL create a database backup before applying migrations
4. WHEN migrations complete successfully, THE CD_Pipeline SHALL log the applied migrations to the Audit_Log
5. THE CD_Pipeline SHALL verify database connectivity to civicfix database using credentials (cdiu8226_nyemb) before applying migrations

### Requirement 5: Vérification Post-Déploiement

**User Story:** En tant qu'administrateur système, je veux vérifier automatiquement que le déploiement a réussi, afin de détecter rapidement les problèmes en production.

#### Acceptance Criteria

1. WHEN deployment completes, THE CD_Pipeline SHALL perform health checks on nyem.cdwfs.net within 30 seconds
2. THE CD_Pipeline SHALL verify that the application responds with HTTP 200 status code on the homepage
3. THE CD_Pipeline SHALL verify that the admin interface is accessible at /admin/
4. IF health checks fail, THEN THE CD_Pipeline SHALL trigger the Rollback_Mechanism automatically
5. WHEN health checks pass, THE CD_Pipeline SHALL mark the deployment as successful in the Audit_Log

### Requirement 6: Mécanisme de Rollback

**User Story:** En tant qu'administrateur système, je veux pouvoir revenir automatiquement à la version précédente en cas d'échec, afin de minimiser l'impact sur les utilisateurs.

#### Acceptance Criteria

1. IF deployment or health checks fail, THEN THE Rollback_Mechanism SHALL restore the previous working version within 2 minutes
2. THE Rollback_Mechanism SHALL restore the previous code version using Git commit hash
3. THE Rollback_Mechanism SHALL restore the database backup if migrations were applied
4. WHEN rollback completes, THE Notification_System SHALL alert the team with failure details and rollback status
5. THE Rollback_Mechanism SHALL log the rollback event to the Audit_Log with timestamp and reason

### Requirement 7: Notifications et Alertes

**User Story:** En tant que membre de l'équipe, je veux être notifié des événements importants du pipeline CI/CD, afin de réagir rapidement aux problèmes.

#### Acceptance Criteria

1. WHEN a deployment succeeds, THE Notification_System SHALL send a success notification with commit details and deployment time
2. WHEN a deployment fails, THE Notification_System SHALL send a failure notification with error logs and affected commit
3. WHEN a Deployment_Blocker is detected by SonarQube_Analyzer, THE Notification_System SHALL send an alert with vulnerability details
4. THE Notification_System SHALL support multiple notification channels including GitHub notifications and email
5. THE Notification_System SHALL include direct links to SonarQube reports, GitHub Actions logs, and production site in notifications

### Requirement 8: Traçabilité et Audit

**User Story:** En tant que responsable projet, je veux tracer tous les déploiements et leurs résultats, afin de maintenir un historique complet et faciliter les audits.

#### Acceptance Criteria

1. THE CD_Pipeline SHALL record each deployment attempt in the Audit_Log with timestamp, commit hash, deployer, and result status
2. THE Audit_Log SHALL include SonarQube_Analyzer results for each deployment including vulnerability count and Quality_Gate status
3. THE Audit_Log SHALL be accessible via GitHub Actions history for at least 90 days
4. WHEN a rollback occurs, THE Audit_Log SHALL record the rollback event with reason and restored version
5. THE CD_Pipeline SHALL tag successful deployments in Git with format "deploy-YYYY-MM-DD-HHmmss"

### Requirement 9: Gestion des Secrets et Sécurité

**User Story:** En tant qu'administrateur sécurité, je veux que les credentials et secrets soient gérés de manière sécurisée, afin de protéger l'accès au serveur de production.

#### Acceptance Criteria

1. THE CD_Pipeline SHALL retrieve all sensitive credentials from GitHub Secrets encrypted storage
2. THE CD_Pipeline SHALL use SSH key-based authentication for O2Switch_Server connections
3. THE CD_Pipeline SHALL never log or expose credentials in build logs or error messages
4. THE CD_Pipeline SHALL use environment-specific configurations loaded from .env.production file
5. THE CD_Pipeline SHALL validate that required secrets exist before starting deployment

### Requirement 10: Gestion des Fichiers Statiques et Media

**User Story:** En tant que développeur, je veux que les fichiers statiques soient collectés et déployés automatiquement, afin que l'interface utilisateur fonctionne correctement après déploiement.

#### Acceptance Criteria

1. WHEN deploying to O2Switch_Server, THE CD_Pipeline SHALL execute collectstatic command to gather all static files
2. THE CD_Pipeline SHALL set correct permissions (755) on staticfiles and media directories
3. THE CD_Pipeline SHALL preserve existing media files uploaded by users during deployment
4. THE CD_Pipeline SHALL verify that static files are accessible via HTTPS after deployment
5. IF collectstatic fails, THEN THE CD_Pipeline SHALL halt deployment and report the error

### Requirement 11: Optimisation des Performances du Pipeline

**User Story:** En tant que développeur, je veux que le pipeline CI/CD soit rapide et efficace, afin de réduire le temps entre commit et déploiement.

#### Acceptance Criteria

1. THE CI_Pipeline SHALL cache Python dependencies between builds to reduce installation time
2. THE CI_Pipeline SHALL execute SonarQube_Analyzer scan and deployment preparation in parallel when possible
3. THE CD_Pipeline SHALL use incremental deployment strategies to minimize downtime
4. THE CI_Pipeline SHALL complete the full cycle from commit to production deployment within 10 minutes for passing builds
5. THE CD_Pipeline SHALL restart Passenger application using touch tmp/restart.txt for zero-downtime deployment

### Requirement 12: Support Multi-Environnement

**User Story:** En tant qu'administrateur système, je veux distinguer les déploiements selon les branches, afin de supporter différents environnements (staging, production).

#### Acceptance Criteria

1. WHEN a commit is pushed to the main branch, THE CD_Pipeline SHALL deploy to production environment on O2Switch_Server
2. WHEN a commit is pushed to a staging branch, THE CD_Pipeline SHALL deploy to staging environment if configured
3. THE CD_Pipeline SHALL load environment-specific configuration from .env.production for production deployments
4. THE CD_Pipeline SHALL apply different Quality_Gate thresholds based on target environment
5. WHERE a staging environment exists, THE CD_Pipeline SHALL require manual approval before production deployment

