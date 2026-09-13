# Connecteur Grist

## Rôle

Ce connecteur permet à MyIA de consulter des données structurées dans Grist
et, si cela est autorisé, de créer ou modifier des éléments. Il est destiné
aux usages de La Suite numérique.

## Capacités et cas d'usage

Le connecteur peut notamment :

- parcourir les organisations, espaces, documents et tables ;
- consulter les colonnes et les enregistrements ;
- effectuer des requêtes sur les données ;
- selon les droits accordés, créer, modifier, supprimer ou exporter des
  éléments, gérer des pièces jointes et des webhooks.

Exemples de demandes à tester dans OpenWebUI :

> Donne-moi la liste des organisations Grist auxquelles j'ai accès.

> Dans l'espace [nom de l'espace], liste les documents disponibles puis indique les tables du document [nom du document].

> Dans la table [nom de la table], affiche les cinq premiers enregistrements sans modifier les données.

Les requêtes SQL et les actions d'écriture doivent être considérées comme
potentiellement sensibles, même lorsqu'elles semblent simples.

## Installation

Préparer une clé API Grist dédiée au connecteur. La conserver dans
l'environnement ou un gestionnaire de secrets, jamais dans le dépôt.

- Clé obligatoire : `GRIST_API_KEY`
- URL API facultative : `GRIST_API_URL`
- URL par défaut : `https://docs.getgrist.com/api`
- URL La Suite numérique : `https://grist.numerique.gouv.fr/api`

Ne pas utiliser l'URL d'une page Grist contenant `/o/.../ws/...` comme URL API.

Le serveur Grist peut fonctionner en STDIO ou en Streamable HTTP. Pour une
déclaration dans LiteLLM, utiliser le mode Streamable HTTP et exposer le
serveur local sur :

```text
http://127.0.0.1:8000/mcp
```

Dans LiteLLM, ouvrir **MCP Servers > Add New MCP Server** et renseigner :

| Champ | Valeur |
|---|---|
| Nom | `grist` |
| MCP Server URL / Server URL | l'URL MCP du serveur Grist |
| Transport | **Streamable HTTP** |
| Authentification | **API Key** |
| Valeur d'authentification | la clé API Grist, dans le champ secret |
| GitHub / Source URL | `https://github.com/nic01asFr/mcp-server-grist` |

Avec Docker Desktop, si Grist MCP est lancé sur le Mac, saisir
`http://host.docker.internal:8000/mcp` dans LiteLLM. Le serveur écoute alors
sur `http://127.0.0.1:8000/mcp` côté Mac. Ne pas saisir `localhost` dans
LiteLLM, car il désignerait le conteneur LiteLLM.

Le transport SSE est déprécié par le projet Grist et ne doit pas être choisi
pour une nouvelle installation. Pour le mode STDIO, consulter la
[documentation du connecteur](../../README.md#grist--la-suite-numérique).

## Tests

1. Dans LiteLLM, vérifier que le serveur est joignable et que les outils sont
   découverts.
2. Dans OpenWebUI, envoyer les demandes de lecture ci-dessus avec un espace et
   un document de test.
3. Vérifier successivement les organisations, espaces, documents, tables et
   enregistrements.
4. Vérifier une lecture sans données sensibles.
5. Demander une modification, par exemple :

   > Ajoute une ligne de test dans cette table Grist.

   L'action doit être refusée ou soumise à une confirmation explicite selon la
   politique configurée. Ne tester une écriture que dans un document dédié.

Les créations, modifications, suppressions, imports, changements de droits,
téléversements et webhooks doivent être autorisés par le bridge, confirmés par
l'utilisateur et journalisés sans clé ni contenu sensible.

## Limites et dépannage

- Sans `GRIST_API_KEY`, le serveur ne peut pas accéder à Grist.
- Si l'instance est incorrecte, vérifier `GRIST_API_URL` et utiliser l'URL API,
  pas une URL de navigation Grist.
- Si aucun outil n'est découvert, vérifier le lancement du serveur, le chemin
  `/mcp` et le transport Streamable HTTP.
- Si LiteLLM ne joint pas le serveur sous Docker Desktop, remplacer
  `127.0.0.1` par `host.docker.internal` dans l'URL saisie dans LiteLLM.
- Si une action est refusée, vérifier les droits de la clé et la règle de
  confirmation du bridge.