# Installer un connecteur MCP

Ce guide explique comment ajouter les connecteurs du POC à une instance MyIA. Il s'adresse aux personnes qui administrent MyIA, sans supposer une connaissance du développement MCP.

## Avant de commencer

Vérifier que :

- MyIA et LiteLLM fonctionnent déjà ;
- l'administrateur dispose d'un accès à la configuration des outils MCP ;
- les secrets éventuels sont stockés dans la configuration locale ou dans un gestionnaire de secrets ;
- le connecteur choisi est compatible avec l'usage prévu et les règles de l'établissement.

Ne placez jamais une clé réelle dans le dépôt, un fichier versionné, une capture d'écran ou un prompt.

## Parcours général

L'installation d'un connecteur suit toujours le même parcours :

1. choisir le connecteur dans le catalogue ;
2. lire sa fiche de sécurité et ses prérequis ;
3. déclarer sa connexion dans la configuration MCP ;
4. limiter les outils et les comptes accessibles ;
5. activer le connecteur dans l'administration MyIA ;
6. tester d'abord une action de lecture ;
7. activer les écritures uniquement avec confirmation explicite et audit.

Les utilisateurs finaux n'ont pas à installer ni configurer les connecteurs.

## Installer data.gouv.fr

Le serveur data.gouv.fr est déjà hébergé. Il n'y a donc pas de programme à installer sur le serveur MyIA.

### Déclaration

Dans cette installation, le serveur est ajouté depuis l'interface d'administration LiteLLM :

1. Ouvrir `http://localhost:4000/ui/`.
2. Se connecter avec la clé maître `LITELLM_MASTER_KEY` définie dans le fichier `.env` de MyIA.
3. Ouvrir **MCP Servers** puis **Add New MCP Server**.
4. Renseigner les champs suivants :

| Champ | Valeur |
|---|---|
| Nom | `datagouv` |
| MCP Server URL / Server URL | `https://mcp.data.gouv.fr/mcp` |
| Transport | Streamable HTTP |
| Authentification | Aucune |
| GitHub / Source URL | `https://github.com/datagouv/datagouv-mcp` |

Le champ **MCP Server URL** est l'adresse utilisée pour appeler le serveur. Le champ **GitHub / Source URL** est seulement la référence du projet source et ne remplace pas l'endpoint MCP.

Enregistrer le serveur, puis vérifier que LiteLLM découvre ses outils.

Pour un client MCP qui accepte une configuration JSON, l'équivalent est :

```json
{
  "url": "https://mcp.data.gouv.fr/mcp",
  "type": "http"
}
```

### Vérification

1. Vérifier que le serveur est joignable depuis LiteLLM.
2. Vérifier que les outils sont découverts.
3. Ouvrir `http://localhost:3000`, créer une nouvelle conversation et sélectionner le modèle configuré dans MyIA.
4. Envoyer une demande explicite, par exemple :

  > Recherche sur data.gouv.fr des jeux de données publics concernant les effectifs étudiants en France. Donne-moi les titres et les liens des trois résultats les plus pertinents.

  MyIA doit alors utiliser un outil de recherche data.gouv.fr et afficher les résultats dans la conversation.
5. Dans LiteLLM, ouvrir la fiche du serveur et consulter la liste des outils découverts. Les outils attendus sont des outils de recherche ou de consultation, par exemple `search_datasets`, `search_organizations`, `get_dataset_info`, `list_dataset_resources` et `get_resource_info`.
6. Vérifier qu'aucun outil de création, modification, suppression, import ou envoi n'est présent. Pour data.gouv.fr, la liste doit être en lecture seule.
7. Depuis MyIA, demander par exemple :

  > Modifie ce jeu de données sur data.gouv.fr.

  MyIA doit indiquer qu'il peut seulement consulter les données et ne doit appeler aucun outil d'écriture.
8. Vérifier dans les logs qu'aucune clé n'est envoyée au serveur data.gouv.fr.

Aucune clé n'est requise pour l'instance publique documentée. Une installation locale relève de la documentation du projet [datagouv/datagouv-mcp](https://github.com/datagouv/datagouv-mcp).

## Installer Grist

Grist nécessite une instance Grist accessible et une clé API dédiée. L'URL par défaut documentée par le serveur est `https://docs.getgrist.com/api` ; une autre instance peut être indiquée avec `GRIST_API_URL`.

Pour une instance La Suite numérique, utiliser l'URL de base de l'API, généralement :

```text
https://grist.numerique.gouv.fr/api
```

Ne pas utiliser directement l'URL d'une page d'espace ou de document telle que `/o/.../ws/...`. Le serveur MCP ajoute lui-même les chemins d'API (`/orgs`, `/workspaces`, `/docs`) à l'URL configurée.

### Préparer la clé

1. Créer une clé API dédiée au connecteur.
2. Lui accorder uniquement les droits nécessaires.
3. La stocker dans le gestionnaire de secrets ou l'environnement du service MCP.
4. Ne jamais la copier dans `catalog.yaml`, un fichier YAML versionné ou le README.

### Déclaration STDIO

Le mode STDIO lance le serveur localement avec `uvx` :

```json
{
  "command": "uvx",
  "args": ["mcp-server-grist"],
  "env": {
    "GRIST_API_KEY": "${GRIST_API_KEY}",
    "GRIST_API_URL": "https://grist.numerique.gouv.fr/api"
  }
}
```

Le client MCP doit remplacer `${GRIST_API_KEY}` par la valeur conservée dans son environnement, sans l'écrire dans le fichier partagé.

### Déclaration Streamable HTTP

Pour un lancement local en HTTP, le projet upstream documente :

```text
http://127.0.0.1:8000/mcp
```

Ce mode doit rester local pendant le POC. Pour une exposition distante, ajouter HTTPS, contrôle d'accès et validation de l'origine. Le transport SSE est déprécié par le projet upstream et ne doit pas être choisi pour une nouvelle installation.

### Déclaration dans LiteLLM

Pour la recette avec LiteLLM :

1. Ouvrir **MCP Servers** puis **Add New MCP Server**.
2. Donner un nom au serveur, par exemple `grist`.
3. Coller l'URL MCP dans le champ **MCP Server URL / Server URL**.
4. Sélectionner le transport **Streamable HTTP**.
5. Choisir le mode d'authentification **API Key**.
6. Coller la clé Grist dans le champ secret prévu pour la valeur d'authentification.
7. Renseigner l'URL du dépôt dans **GitHub / Source URL** : `https://github.com/nic01asFr/mcp-server-grist`.
8. Enregistrer, puis vérifier que LiteLLM découvre les outils.

La clé saisie dans LiteLLM remplace alors la configuration `GRIST_API_KEY` du processus local. Ne renseignez pas la clé dans `catalog.yaml`, dans un manifeste YAML, dans le README ou dans une conversation.

### Vérification

1. Démarrer le serveur Grist avec la configuration retenue.
2. Vérifier que le serveur est joignable.
3. Découvrir les outils.
4. Tester `list_organizations`.
5. Parcourir un espace, un document et une table de test.
6. Vérifier une lecture sans données sensibles.
7. Tester une écriture uniquement dans un document de test, après confirmation explicite.

## Autoriser les outils

Commencer avec les outils de lecture. Pour Grist, les créations, modifications, suppressions, changements de droits, imports, téléversements et webhooks doivent être bloqués sans confirmation humaine.

Le bridge ou la couche d'administration doit conserver la décision d'autorisation et un audit sans clé ni contenu sensible.

## Désactiver ou retirer un connecteur

Pour désactiver un connecteur :

1. désactiver son entrée dans la configuration MCP ;
2. retirer son accès de MyIA ;
3. arrêter le processus ou le conteneur associé ;
4. conserver les journaux d'audit nécessaires ;
5. révoquer la clé API si le connecteur n'est plus utilisé.

La désactivation ne doit pas supprimer les données de l'application cible.

## Dépannage rapide

| Symptôme | Vérification |
|---|---|
| Serveur non découvert | URL, transport choisi et redémarrage du client MCP |
| data.gouv.fr inaccessible | disponibilité de `https://mcp.data.gouv.fr/mcp` et accès réseau sortant |
| Grist refuse la connexion | `GRIST_API_KEY`, `GRIST_API_URL` et droits de la clé |
| Outils d'écriture absents | droits Grist, outils activés et règle de confirmation |
| HTTP local inaccessible | adresse `127.0.0.1`, port `8000` et chemin `/mcp` |
