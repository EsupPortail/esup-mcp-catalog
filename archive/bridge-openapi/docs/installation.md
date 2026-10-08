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

Utiliser une image LiteLLM sur un tag stable et épinglé (par exemple
`ghcr.io/berriai/litellm:v1.83.7-stable` ou plus récent), pas
`main-latest` : ce tag évolue en continu et certaines de ses versions ont
un bug interne (schéma Prisma désynchronisé du code) qui bloque la
création ou l'édition d'un serveur MCP avec une erreur `Could not find
field` ou `MissingRequiredValueError`. Si l'erreur apparaît malgré un tag
stable, réessayer avec le tag stable suivant plutôt que de chercher un
correctif applicatif.

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

Pour corriger un serveur MCP mal configuré, préférer le **supprimer et le
recréer** plutôt que le modifier : sur les versions de LiteLLM testées,
l'édition d'un serveur existant échoue parfois avec une erreur Prisma
(`data.credentials`) alors que la création fonctionne normalement.

La configuration MCP se fait dans LiteLLM. OpenWebUI sert d'interface de
conversation et ne doit pas recevoir les clés des services raccordés.

La déclaration dans LiteLLM est enregistrée dans sa base de données. Pour
utiliser les outils dans OpenWebUI, lancer également le
[bridge MCP vers OpenAPI](../bridge/README.md), puis l'ajouter dans la page
**Panneau d'administration > Réglages > Intégrations** d'OpenWebUI.

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
3. Dans **Panneau d'administration > Réglages > Connexions**, vérifier que
   LiteLLM est accessible et que le modèle configuré est disponible.
4. Ouvrir une nouvelle conversation et sélectionner ce modèle.

## Ajouter le bridge dans OpenWebUI

Depuis le dossier `bridge` :

```bash
cp .env.bridge.example .env.bridge
chmod 600 .env.bridge
```

Éditer `.env.bridge` avant de démarrer : remplacer `BRIDGE_API_KEY` par une
valeur générée (`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`)
et ajuster `MCP_SERVERS_JSON` selon les connecteurs réellement utilisés.
Voir le [README du bridge](../bridge/README.md) pour le détail.

```bash
docker compose up -d
```

Dans **Panneau d'administration > Réglages > Intégrations > Gérer les
serveurs d'outils** (nommé *Tools > Add connection* dans les versions plus
anciennes d'OpenWebUI), ajouter **une connexion par serveur MCP configuré**
(pas une seule connexion regroupant tout, qui empêcherait de choisir un
connecteur à la fois dans le sélecteur d'outils) :

| Champ | Valeur |
|---|---|
| Type | OpenAPI |
| Nom d'utilisateur | nom du connecteur, ex. `data.gouv.fr` |
| URL | `http://host.docker.internal:8090/servers/{nom}` (`{nom}` = clé du serveur dans `MCP_SERVERS_JSON`, ex. `datagouv`) |
| Auth | Bearer |
| Clé API | la valeur de `BRIDGE_API_KEY` dans `.env.bridge` |

Voir le [README du bridge](../bridge/README.md#connexion-openwebui) pour le
détail (champ « Nom d'utilisateur » trompeur, piège `/openapi.json`, et
pourquoi un rechargement complet du navigateur est nécessaire après avoir
ajouté une connexion).

Répéter pour chaque connecteur, enregistrer, puis vérifier que les outils
découverts apparaissent dans le sélecteur d'outils. Le bridge doit être
redémarré après toute modification de `.env.bridge`.

En copiant la clé API depuis un fichier ou un terminal, vérifier qu'elle
n'est pas tronquée (fin de ligne coupée à l'affichage) : une clé
incomplète produit une erreur 401 côté bridge qui ressemble, dans la
réponse du modèle, à un problème d'authentification chez le fournisseur
de données plutôt que sur le bridge lui-même.

## Fiabiliser l'usage des outils par le modèle

Un modèle peut appeler les outils correctement pour une demande simple et
pourtant échouer sur une demande qui combine plusieurs outils : il
n'enchaîne pas toujours les appels tout seul et peut décrire une
procédure manuelle ou halluciner un script au lieu de continuer à utiliser
les outils disponibles. Deux réglages, faits dans **Espace de travail >
Modèles** (icône en haut de la barre latérale, à ne pas confondre avec
l'onglet *Modèles* du panneau d'administration, qui gère la visibilité des
modèles) en éditant la fiche du modèle utilisé, réduisent nettement ce
risque :

1. **Réglages avancés > Appel de fonction** (*Function Calling*) : passer
   de `Par défaut` à `Natif`.
2. **Prompt système** (*System Prompt*) : écrire explicitement la
   procédure attendue pour les tâches récurrentes plutôt qu'une
   instruction générique.

Voir le [cas d'usage combiné data.gouv.fr → Grist](cas-usage-datagouv-grist.md)
pour un exemple complet, avec le system prompt qui a fonctionné et les
limites rencontrées.

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