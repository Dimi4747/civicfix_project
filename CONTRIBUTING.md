# Contributing to KABA-DELIVERY

## Conventional Commits

Nous utilisons la convention [Conventional Commits](https://www.conventionalcommits.org/).

Format : `<type>(<scope optionnel>): <description>`

Types courants :
- `feat`: nouvelle fonctionnalité
- `fix`: correction d'un bug
- `docs`: documentation
- `chore`: maintenance, config
- `refactor`: modification sans changement fonctionnel
- `test`: ajout ou correction de tests

Exemples :
- `feat(api): add delivery endpoint`
- `fix(login): handle timeout error`

## Branches

- `main` : production, protégée (PR uniquement)
- `develop` : intégration
- `feature/*` : nouvelles fonctionnalités
- `hotfix/*` : corrections urgentes

## Processus

1. Crée une branche depuis `develop`
2. Fais tes commits en respectant la convention
3. Ouvre une Pull Request vers `develop` ou `main` (après validation)
4. Attends l'approbation d'au moins un pair et la réussite des tests CI