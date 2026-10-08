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
- URL obligatoire : `GRIST_API_URL=https://grist.numerique.gouv.fr/api`

`GRIST_API_URL` n'est pas optionnelle : le serveur `mcp-server-grist` pointe
par défaut vers `https://docs.getgrist.com/api` (le SaaS public GetGrist), pas
vers La Suite numérique. Sans cette valeur, une clé pourtant valide pour
`grist.numerique.gouv.fr` est rejetée comme invalide. Pour une instance Grist
locale ou une autre instance, adapter cette URL en conséquence. Ne pas
utiliser l'URL d'une page Grist contenant `/o/.../ws/...` comme URL API.

Le serveur MCP Grist peut fonctionner en STDIO ou en Streamable HTTP. La
configuration de l'instance Grist reste la même dans les deux cas. OpenWebUI
ne sait se connecter qu'en Streamable HTTP : utiliser cette URL, celle du
serveur MCP fourni par l'établissement.

Pour un déploiement local, [`grist-mcp/`](../../grist-mcp/README.md) lance
ce serveur automatiquement, joignable sous `http://127.0.0.1:8000/mcp`
depuis le Mac et `http://grist-mcp:8000/mcp` depuis les autres conteneurs du
même réseau Docker.

Dans **Panneau d'administration > Réglages > Intégrations > Serveurs
d'outils externes** d'OpenWebUI, ajouter une connexion :

| Champ | Valeur |
|---|---|
| Type | **MCP (Streamable HTTP)** |
| Nom | `grist` |
| URL | l'URL MCP du serveur Grist |
| Authentification | selon le déploiement, voir ci-dessous |

Deux cas selon qui héberge le serveur MCP Grist :

- **Serveur partagé par l'établissement** : l'authentification se fait par clé
  transmise à chaque appel. Choisir **Bearer** et coller la clé API Grist
  dans le champ secret.
- **Serveur lancé localement** (`grist-mcp/`, `GRIST_API_KEY` dans son
  propre environnement) : le serveur porte déjà la clé, aucune
  authentification supplémentaire n'est nécessaire côté OpenWebUI. Choisir
  **Aucune**.

La *liste de filtrage des noms de fonctions* de la connexion peut être
utilisée pour exclure les outils Grist destructifs ou d'administration
(suppression de documents, gestion des droits) de cette connexion — voir
les noms d'outils exacts exposés avant de composer la liste.

Avec Docker Desktop, si le serveur MCP Grist tourne sur le Mac
(`grist-mcp/` ou processus local), saisir
`http://host.docker.internal:8000/mcp`. Ne pas saisir `localhost`, car il
désignerait le conteneur OpenWebUI lui-même.

Le transport SSE est déprécié par le projet Grist et ne doit pas être choisi
pour une nouvelle installation. Pour le mode STDIO, consulter la
[documentation du projet Grist](https://github.com/nic01asFr/mcp-server-grist#readme).

Déclarer aussi ce serveur dans LiteLLM reste possible mais facultatif — voir
le [guide d'installation](../installation.md) pour la distinction entre les
deux étapes.

## Tests

1. Dans OpenWebUI, vérifier sur l'écran de la connexion que le serveur est
   joignable et que les outils sont découverts.
2. Dans OpenWebUI, envoyer les demandes de lecture ci-dessus avec un espace et
   un document de test.
3. Vérifier successivement les organisations, espaces, documents, tables et
   enregistrements.
4. Vérifier une lecture sans données sensibles.
5. Demander une modification, par exemple :

   > Ajoute une ligne de test dans cette table Grist.

   OpenWebUI ne demande pas de confirmation avant d'écrire : l'action
   s'exécute directement si la clé API Grist le permet. Ne tester une écriture
   que dans un document Grist dédié et jetable, avec une clé dont les droits
   sont limités à ce document.

Les créations, modifications, suppressions, imports, changements de droits,
téléversements et webhooks devront être confirmés par l'utilisateur et
journalisés sans clé ni contenu sensible : ce contrôle n'est pas encore
construit (voir feuille de route). Tant qu'il ne l'est pas, seules la clé
API Grist et la liste de filtrage des noms de fonctions de la connexion
limitent ce que le connecteur peut faire.

## Limites et dépannage

- Sans `GRIST_API_KEY`, le serveur ne peut pas accéder à Grist.
- Si l'instance est incorrecte, vérifier que l'URL par défaut est
   `https://grist.numerique.gouv.fr/api`, ou que `GRIST_API_URL` pointe vers
   l'URL API de l'instance choisie, pas vers une URL de navigation Grist.
- Si aucun outil n'est découvert, vérifier le lancement du serveur, le chemin
  `/mcp` et le transport Streamable HTTP.
- Si OpenWebUI ne joint pas le serveur sous Docker Desktop, remplacer
  `127.0.0.1` par `host.docker.internal` dans l'URL de la connexion.
- Si une action est refusée, vérifier les droits de la clé Grist.
- `id` est un nom de colonne réservé par Grist (identifiant de ligne
  généré automatiquement) : une insertion (`add_grist_records`) contenant
  une colonne `id` échoue avec `Invalid column "id"`. Renommer ou retirer
  cette colonne dans les données à insérer avant l'appel.
- Si le modèle décrit une procédure manuelle ou un script au lieu
  d'appeler les outils, voir le [cas d'usage combiné avec
  data.gouv.fr](../cas-usage-datagouv-grist.md) : un system prompt dédié
  et le mode Function Calling natif d'OpenWebUI corrigent ce
  comportement.