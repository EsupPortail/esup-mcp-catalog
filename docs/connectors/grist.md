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
- URL API : `https://grist.numerique.gouv.fr/api`
- URL de remplacement pour une autre instance : `GRIST_API_URL`

L'instance Grist utilisée par défaut est celle de La Suite numérique. Pour une
instance Grist locale ou une autre instance, remplacer la valeur de
`GRIST_API_URL`. Ne pas utiliser l'URL d'une page Grist contenant
`/o/.../ws/...` comme URL API.

Le serveur MCP Grist peut fonctionner en STDIO ou en Streamable HTTP. La
configuration de l'instance Grist reste la même dans les deux cas. Pour la
configuration par défaut avec LiteLLM, utiliser l'URL Streamable HTTP du
serveur MCP fourni par l'établissement.

Si l'établissement lance lui-même ce processus MCP sur le poste local, il peut
exposer :

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

Ne pas renseigner le champ **GitHub / Source URL** : sur certaines builds de
LiteLLM (`main-latest`), ce champ envoie un attribut `source_url` que le
schéma de la base ne connaît pas encore, ce qui bloque la création avec
l'erreur `Could not find field at createOneLiteLLM_MCPServerTable.data.source_url`.
Laisser le champ vide pour contourner le problème.

Avec Docker Desktop, si le processus MCP Grist est lancé sur le Mac, saisir
`http://host.docker.internal:8000/mcp` dans LiteLLM. Le serveur écoute alors
sur `http://127.0.0.1:8000/mcp` côté Mac. Ne pas saisir `localhost` dans
LiteLLM, car il désignerait le conteneur LiteLLM.

Le transport SSE est déprécié par le projet Grist et ne doit pas être choisi
pour une nouvelle installation. Pour le mode STDIO, consulter la
[documentation du projet Grist](https://github.com/nic01asFr/mcp-server-grist#readme).

La déclaration dans LiteLLM ne suffit pas à rendre automatiquement les outils
visibles dans OpenWebUI. OpenWebUI doit aussi être configuré comme client MCP,
ou une intégration doit transmettre la définition du serveur dans le champ
`tools` de la requête au modèle. Voir le [guide d'installation](../installation.md)
pour distinguer ces deux étapes.

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

   Le bridge actuel ne demande pas de confirmation avant d'écrire : l'action
   s'exécute directement si la clé API Grist le permet. Ne tester une écriture
   que dans un document Grist dédié et jetable, avec une clé dont les droits
   sont limités à ce document.

Les créations, modifications, suppressions, imports, changements de droits,
téléversements et webhooks devront être autorisés par le bridge, confirmés par
l'utilisateur et journalisés sans clé ni contenu sensible : ce contrôle n'est
pas encore construit (voir feuille de route). Tant qu'il ne l'est pas, seule
la clé API Grist limite ce que le connecteur peut faire.

## Limites et dépannage

- Sans `GRIST_API_KEY`, le serveur ne peut pas accéder à Grist.
- Si l'instance est incorrecte, vérifier que l'URL par défaut est
   `https://grist.numerique.gouv.fr/api`, ou que `GRIST_API_URL` pointe vers
   l'URL API de l'instance choisie, pas vers une URL de navigation Grist.
- Si aucun outil n'est découvert, vérifier le lancement du serveur, le chemin
  `/mcp` et le transport Streamable HTTP.
- Si LiteLLM ne joint pas le serveur sous Docker Desktop, remplacer
  `127.0.0.1` par `host.docker.internal` dans l'URL saisie dans LiteLLM.
- Si une action est refusée, vérifier les droits de la clé et la règle de
  confirmation du bridge.