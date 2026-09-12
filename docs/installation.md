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

Ajouter le serveur dans la configuration MCP de MyIA ou de LiteLLM avec :

```json
{
  "url": "https://mcp.data.gouv.fr/mcp",
  "type": "http"
}
```

### Vérification

1. Enregistrer la configuration.
2. Vérifier que le serveur est joignable.
3. Vérifier que les outils sont découverts.
4. Lancer une recherche simple de jeu de données.
5. Vérifier que seuls des outils de lecture sont proposés.

Aucune clé n'est requise pour l'instance publique documentée. Une installation locale relève de la documentation du projet [datagouv/datagouv-mcp](https://github.com/datagouv/datagouv-mcp).

## Installer Grist

Grist nécessite une instance Grist accessible et une clé API dédiée. L'URL par défaut documentée par le serveur est `https://docs.getgrist.com/api` ; une autre instance peut être indiquée avec `GRIST_API_URL`.

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
    "GRIST_API_URL": "https://docs.getgrist.com/api"
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
