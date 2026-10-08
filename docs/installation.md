# Installer un connecteur MCP

Ce guide décrit le parcours commun pour ajouter un connecteur du catalogue à
une instance MyIA déjà lancée. Les réglages propres à chaque connecteur sont
documentés dans sa fiche :

- [Connecteur data.gouv.fr](connectors/datagouv.md) ;
- [Connecteur Grist](connectors/grist.md) ;
- [Connecteur HAL](connectors/hal.md) ;
- [Connecteur OpenAlex](connectors/openalex.md) ;
- [Connecteur Légifrance](connectors/legifrance.md).

Les utilisateurs finaux n'installent ni ne configurent les connecteurs.

## Préparer l'installation

Avant de commencer :

- OpenWebUI **≥ v0.6.31** est accessible sur `http://127.0.0.1:3000` (c'est
  la version à partir de laquelle OpenWebUI sait se connecter nativement à
  un serveur MCP en Streamable HTTP — vérifier la version dans le panneau
  "À propos" de l'administration, ou via `/_app/version.json`) ;
- LiteLLM est accessible sur `http://127.0.0.1:4000` ;
- le serveur MCP choisi et l'application cible sont accessibles ;
- les secrets sont conservés dans l'environnement ou un gestionnaire de
  secrets, jamais dans le dépôt, les journaux ou les conversations.

Le support MCP natif d'OpenWebUI est qualifié d'expérimental par sa propre
documentation, qui indique que l'intégration OpenAPI reste la mieux
maintenue par son équipe. Si une connexion MCP se comporte de façon
instable ou disparaît après une mise à jour d'OpenWebUI, l'architecture
précédente (bridge de traduction MCP→OpenAPI) reste documentée dans
[`archive/bridge-openapi/`](../archive/bridge-openapi/ARCHIVE.md).

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

## Déclarer le connecteur dans LiteLLM (facultatif)

Cette étape est **facultative** : elle ne concerne que les usages de
LiteLLM en tant que passerelle MCP pour des consommateurs API directs, hors
OpenWebUI. Elle n'est **pas nécessaire** pour que les outils MCP
apparaissent dans les conversations OpenWebUI — voir la section suivante.

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

## Déclarer la connexion MCP dans OpenWebUI

Dans **Panneau d'administration > Réglages > Intégrations > Serveurs
d'outils externes**, cliquer sur **+ Ajouter une connexion** — **une
connexion par connecteur** (pas une connexion regroupant plusieurs serveurs
MCP : le sélecteur d'outils d'OpenWebUI active/désactive une connexion
entière, pas un outil individuel ; une connexion par connecteur permet de
choisir au cas par cas).

| Champ | Valeur |
|---|---|
| Type | **MCP (Streamable HTTP)** |
| ID | identifiant technique du connecteur, ex. `datagouv` — reprendre le `id` du [manifeste](../connectors/) correspondant |
| Nom | nom affiché du connecteur, ex. `data.gouv.fr` |
| URL | l'URL MCP du connecteur — voir sa fiche |
| Authentification | Aucune / Bearer / Session / OAuth 2.1 selon le connecteur — voir sa fiche |
| Liste de filtrage des noms de fonctions | laisser vide, sauf cas particulier (voir dépannage) |

Répéter pour chaque connecteur, enregistrer, puis vérifier que les outils
découverts apparaissent sur l'écran de la connexion.

**Dépannage :**

- Un champ *Liste de filtrage des noms de fonctions* laissé vide peut
  provoquer une erreur de connexion sur certaines versions d'OpenWebUI ; si
  la connexion échoue sans autre explication, renseigner une simple virgule
  (`,`) dans ce champ. Ce même champ peut aussi être utilisé volontairement
  pour restreindre les outils exposés par une connexion (par exemple
  exclure les outils Grist destructifs ou d'administration).
- En copiant une clé d'authentification depuis un fichier ou un terminal,
  vérifier qu'elle n'est pas tronquée (fin de ligne coupée à l'affichage) :
  une clé incomplète produit une erreur d'authentification qui, dans la
  réponse du modèle, peut ressembler à un problème côté fournisseur de
  données plutôt qu'à une clé mal copiée.

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

1. (si déclaré) vérifier dans LiteLLM que le serveur est joignable et que
   ses outils sont découverts ;
2. vérifier dans OpenWebUI, sur l'écran de la connexion, que les outils
   sont bien découverts (liste non vide) ;
3. ouvrir une conversation, activer la connexion dans le sélecteur
   d'outils, et effectuer une demande de lecture décrite dans la fiche du
   connecteur.

## Tester et sécuriser

Pour le moment, effectuer le test initial du connecteur dans OpenWebUI (et
dans LiteLLM si déclaré) :

1. vérifier que le serveur est joignable et que ses outils sont découverts ;
2. vérifier qu'aucune donnée sensible ni aucun secret n'apparaît dans les
   réponses ou les journaux ;
3. tester une écriture uniquement si elle est prévue, avec confirmation
   explicite et audit.

Les outils et permissions doivent rester limités à l'usage prévu. Toute
action destructive ou toute modification de droits nécessite une confirmation
humaine.

## Désactiver un connecteur

1. Retirer la connexion dans **Panneau d'administration > Réglages >
   Intégrations > Serveurs d'outils externes** d'OpenWebUI.
2. Si déclaré, désactiver ou supprimer l'entrée correspondante dans **MCP
   Servers** de LiteLLM.
3. Arrêter le conteneur associé si le connecteur est auto-hébergé (par
   exemple `grist-mcp`).
4. Révoquer la clé API si elle n'est plus utilisée.

La désactivation ne supprime pas les données de l'application cible.
