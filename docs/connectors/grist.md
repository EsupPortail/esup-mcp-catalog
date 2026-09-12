# Connecteur Grist

## Rôle

Ce connecteur permet à MyIA de consulter et, si l'établissement l'autorise, de manipuler des données structurées dans Grist. Il correspond au premier connecteur envisagé pour les usages de La Suite numérique.

## Source et prérequis

- Dépôt : [nic01asFr/mcp-server-grist](https://github.com/nic01asFr/mcp-server-grist)
- Python : version 3.10 ou supérieure d'après le projet upstream
- Clé obligatoire : `GRIST_API_KEY`
- URL optionnelle : `GRIST_API_URL`
- URL par défaut documentée : `https://docs.getgrist.com/api`

La clé doit être créée et conservée dans la configuration locale ou un gestionnaire de secrets. Elle ne doit jamais être écrite dans ce dépôt.

## Choisir le transport

### STDIO, recommandé en local

Le client lance le serveur directement :

```json
{
  "command": "uvx",
  "args": ["mcp-server-grist"],
  "env": {
    "GRIST_API_KEY": "${GRIST_API_KEY}",
    "GRIST_API_URL": "https://docs.getgrist.com/api"
  }
}
```

### Streamable HTTP

Le projet upstream documente un lancement local sur `127.0.0.1:8000` avec le chemin `/mcp`. Ce mode doit rester limité au réseau local pendant le POC. Toute exposition distante nécessite HTTPS, contrôle d'accès et validation de l'origine.

Le transport SSE est déprécié dans le projet upstream et ne doit pas être choisi pour une nouvelle configuration.

## Capacités

Les outils sont organisés autour de la navigation, des requêtes, des enregistrements, de l'administration, des accès, de l'export, des pièces jointes et des webhooks. Le parcours de découverte recommandé est :

1. organisations ;
2. espaces de travail ;
3. documents ;
4. tables ;
5. colonnes et enregistrements.

## Permissions et confirmations

Activer d'abord les outils de lecture. Toute création, modification, suppression, import, modification de droits, téléversement ou gestion de webhook doit :

- utiliser un compte ou une clé dédiés ;
- être autorisée par le bridge ;
- demander une confirmation explicite à l'utilisateur ;
- être journalisée sans enregistrer la clé ni le contenu sensible.

Les requêtes SQL doivent être traitées comme des opérations potentiellement sensibles, même lorsqu'elles sont présentées comme une simple consultation.

## Test initial

1. Configurer `GRIST_API_KEY` hors du dépôt.
2. Démarrer le serveur en STDIO.
3. Vérifier `list_organizations`, puis parcourir un espace et un document de test.
4. Vérifier la lecture de tables sans données sensibles.
5. Tester une opération d'écriture uniquement avec confirmation et dans un document de test.

## Dépannage

- Clé absente : vérifier `GRIST_API_KEY` dans l'environnement du processus.
- Instance incorrecte : vérifier `GRIST_API_URL`.
- Outils absents : vérifier le lancement `uvx mcp-server-grist` et le transport choisi.
- HTTP inaccessible : vérifier l'écoute sur `127.0.0.1`, le port `8000` et le chemin `/mcp`.
- Action refusée : vérifier les droits de la clé et la règle de confirmation du bridge.
