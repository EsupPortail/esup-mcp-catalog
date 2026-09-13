# Installer un connecteur MCP

Ce guide décrit le parcours commun pour ajouter un connecteur du catalogue à
une instance MyIA déjà lancée. Les réglages propres à chaque connecteur sont
documentés dans sa fiche :

- [Connecteur data.gouv.fr](connectors/datagouv.md) ;
- [Connecteur Grist](connectors/grist.md).

Les utilisateurs finaux n'installent ni ne configurent les connecteurs.

## Préparer l'installation

Avant de commencer :

- LiteLLM est accessible sur `http://127.0.0.1:4000` ;
- OpenWebUI est accessible sur `http://127.0.0.1:3000` ;
- le serveur MCP choisi et l'application cible sont accessibles ;
- les secrets sont conservés dans l'environnement ou un gestionnaire de
  secrets, jamais dans le dépôt, les journaux ou les conversations.

Pour une stack Docker Desktop, un serveur MCP lancé sur le Mac est accessible
depuis un conteneur avec `host.docker.internal`, et non avec `localhost` ou
`127.0.0.1`. La fiche du connecteur indique l'URL à utiliser.

## Déclarer le connecteur

1. Ouvrir `http://127.0.0.1:4000/ui/`.
2. Se connecter avec `LITELLM_MASTER_KEY`.
3. Ouvrir **MCP Servers**, puis **Add New MCP Server**.
4. Reprendre les valeurs indiquées dans la fiche du connecteur : URL MCP,
   transport, authentification et source du projet.
5. Enregistrer, puis vérifier que LiteLLM découvre les outils.

La configuration MCP se fait dans LiteLLM. OpenWebUI sert d'interface de
conversation et ne doit pas recevoir les clés des services raccordés.

La déclaration dans LiteLLM est enregistrée dans sa base de données. Pour
utiliser les outils dans OpenWebUI, lancer également le
[bridge MCP vers OpenAPI](../bridge/README.md), puis l'ajouter dans la page
**Admin > Settings > Tools** d'OpenWebUI.

Le bridge utilise sa propre liste de serveurs dans `.env.bridge` ; il ne lit pas
automatiquement les serveurs enregistrés dans LiteLLM. Il faut donc conserver
les mêmes URLs MCP dans cette configuration.

## Vérifier OpenWebUI

La stack configure normalement OpenWebUI avec LiteLLM :

```text
URL API : http://litellm:4000/v1
Clé    : LITELLM_MASTER_KEY
```

Après le démarrage :

1. Ouvrir `http://127.0.0.1:3000`.
2. Si l'inscription est désactivée, passer temporairement `ENABLE_SIGNUP` à
   `"true"`, redémarrer OpenWebUI, créer le premier compte administrateur,
   puis repasser `ENABLE_SIGNUP` à `"false"`.
3. Dans **Admin Panel > Settings > Connections**, vérifier que LiteLLM est
   accessible et que le modèle configuré est disponible.
4. Ouvrir une nouvelle conversation et sélectionner ce modèle.

## Ajouter le bridge dans OpenWebUI

Depuis le dossier `bridge` :

```bash
cp .env.bridge.example .env.bridge
chmod 600 .env.bridge
docker compose up -d
```

Dans **Admin > Settings > Tools > Add connection**, renseigner :

| Champ | Valeur |
|---|---|
| Type | OpenAPI |
| Nom d'utilisateur | `MCP Catalog` |
| URL | `http://host.docker.internal:8090` |
| Auth | Bearer |
| Clé API | la valeur de `BRIDGE_API_KEY` dans `.env.bridge` |

Ne pas ajouter `/openapi.json` à la fin de l'URL : OpenWebUI l'ajoute lui-même.
Le mettre quand même produit une requête vers `.../openapi.json/openapi.json`,
qui échoue en 404.

Enregistrer, puis vérifier que les outils découverts apparaissent dans la
liste des outils. Le bridge doit être redémarré après toute modification de
`.env.bridge`.

## Vérifier le chemin MCP

Après l'enregistrement dans LiteLLM :

1. vérifier dans LiteLLM que le serveur est joignable et que ses outils sont
   découverts ;
2. vérifier dans le bridge que les outils sont visibles sur
   `http://127.0.0.1:8090/openapi.json` ;
3. vérifier dans OpenWebUI que les outils du bridge apparaissent ;
4. ouvrir une conversation et effectuer une demande de lecture décrite dans la
   fiche du connecteur.

## Tester et sécuriser

Pour le moment, effectuer le test initial du connecteur dans LiteLLM :

1. vérifier que le serveur est joignable et que ses outils sont découverts ;
2. vérifier qu'aucune donnée sensible ni aucun secret n'apparaît dans les
   réponses ou les journaux ;
3. tester une écriture uniquement si elle est prévue, avec confirmation
   explicite et audit.

Les outils et permissions doivent rester limités à l'usage prévu. Toute
action destructive ou toute modification de droits nécessite une confirmation
humaine.

## Désactiver un connecteur

1. Désactiver ou supprimer son entrée dans **MCP Servers** de LiteLLM.
2. Retirer son accès dans la couche d'administration.
3. Arrêter le processus ou le conteneur associé.
4. Révoquer la clé API si elle n'est plus utilisée.

La désactivation ne supprime pas les données de l'application cible.