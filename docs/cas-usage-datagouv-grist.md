# Cas d'usage : importer des données data.gouv.fr dans Grist

Ce document raconte un test réalisé de bout en bout avec les deux connecteurs
du POC : demander à MyIA, en langage naturel, de récupérer des données
publiques sur data.gouv.fr et de les ranger dans un tableau Grist. Il ne
décrit pas une procédure à suivre à la lettre, mais explique ce qui a
bloqué, ce qui a été ajusté, et le résultat obtenu — pour que la prochaine
personne qui tente un scénario du même genre gagne du temps.

## Objectif du test

Vérifier que MyIA peut combiner deux connecteurs dans une seule demande
utilisateur, sans que la personne ait à connaître les noms des outils MCP,
les identifiants techniques (dataset, document Grist) ou la mécanique
interne du bridge.

## Pré-requis

- Les connecteurs [data.gouv.fr](connectors/datagouv.md) et
  [Grist](connectors/grist.md) déclarés dans LiteLLM et actifs dans le
  [bridge](../bridge/README.md).
- Un document Grist de test existant (créé au préalable, avec un nom
  connu de l'utilisateur).

## Ce qui a d'abord échoué

Avec une configuration par défaut (aucun system prompt particulier, mode
Function Calling par défaut d'OpenWebUI), demander directement une tâche
combinée du type *« Cherche un jeu de données sur X et importe-le dans
Grist »* a systématiquement échoué, de deux façons différentes :

1. **Le modèle refusait d'utiliser l'outil d'écriture**, avec une réponse
   du type *« Je ne peux pas créer directement un tableau dans Grist, car
   cela nécessite une action manuelle ou l'API Grist »* — alors que
   l'outil `create_table` était bien exposé et fonctionnel (vérifié en
   l'appelant directement sur le bridge). Le modèle n'avait tout
   simplement pas assez d'informations (l'identifiant interne du document
   Grist, `doc_id`) pour construire l'appel, et au lieu d'aller le
   chercher via `list_documents` ou de le demander, il a répondu par un
   texte générique de refus.
2. **Sur une tâche à plusieurs outils**, le modèle appelait le premier
   outil (`search_datasets`), puis abandonnait l'enchaînement et
   inventait une procédure manuelle, y compris un script Python fictif
   pointant vers `api.grist.com` (mauvais domaine, ne correspond à rien
   dans cette installation) et redemandant une clé API pourtant déjà
   configurée côté serveur.

Le point commun : le modèle utilisé (Mistral Medium via ILaaS) n'est pas
assez agentique pour enchaîner plusieurs appels d'outils sans y être
poussé explicitement, et bascule vers du texte halluciné plutôt que de
continuer à utiliser les outils disponibles.

## Ajustements qui ont fonctionné

Deux réglages, faits côté OpenWebUI dans **Espace de travail > Modèles**
(éditer le modèle utilisé — écran distinct de l'onglet *Modèles* du
panneau d'administration), ont nettement amélioré la fiabilité :

**1. Appel de fonction en mode natif**

Dans **Réglages avancés**, passer *Appel de fonction* (*Function Calling*)
de `Par défaut` (le modèle simule l'appel via du texte, peu fiable) à
`Natif` (appel réel via l'API function-calling du modèle).

**2. Un prompt système qui écrit la procédure à l'avance**

Un prompt générique ("utilise les outils disponibles") ne suffit pas. Ce
qui a fonctionné, c'est d'écrire la recette complète pour ce type de
tâche récurrente, y compris les pièges déjà rencontrés :

> Tu as accès à des outils MCP (data.gouv.fr, Grist). Pour toute action
> possible avec un outil, tu DOIS l'appeler — ne décris jamais une
> procédure manuelle, ne propose jamais de script, de clé API ou de lien
> à suivre toi-même. Si une information manque pour appeler un outil,
> appelle un autre outil pour la trouver, ou pose une question précise à
> l'utilisateur. N'invente jamais d'URL ou de résultat : n'affiche que ce
> qu'un outil a réellement renvoyé.
>
> Quand on te demande d'importer des données de data.gouv.fr dans Grist,
> exécute sans t'arrêter : `search_datasets` → `list_dataset_resources` →
> `query_resource_data` → retire ou renomme toute colonne "id" (réservée
> par Grist, une insertion la contenant est rejetée) → `create_table` si
> la table n'existe pas → `add_grist_records`. Ne t'arrête entre les
> étapes que si une information est réellement ambiguë (plusieurs jeux de
> données possibles, plusieurs documents Grist).

## Résultat

Avec ces deux réglages, la demande suivante — sans nom d'outil, sans
identifiant technique, avec seulement le nom usuel du document Grist — a
été exécutée de bout en bout automatiquement :

> Trouve sur data.gouv.fr un jeu de données sur la réussite des étudiants
> en Polynésie française, et importe ces données dans une nouvelle table
> "etudiants_polynesie" de mon document Grist "testmcp".

Le modèle a résolu seul le nom du document vers son identifiant Grist,
enchaîné les quatre outils sans intervention, et corrigé la colonne `id`
comme indiqué dans le system prompt.

## Limite connue rencontrée : la colonne réservée `id`

Un premier essai d'insertion (`add_grist_records`) a échoué avec l'erreur
`Invalid column "id"` : Grist réserve ce nom de colonne pour son propre
identifiant de ligne, généré automatiquement. Toute donnée externe
contenant une colonne `id` doit être renommée (par exemple `id_source`)
ou retirée avant l'insertion. C'est désormais couvert par le system
prompt ci-dessus, et noté dans les [limites du connecteur
Grist](connectors/grist.md#limites-et-dépannage).

## Limite connue de l'interface : pas de sélection fine des outils

Le sélecteur d'outils d'OpenWebUI, dans la fenêtre de conversation, active
ou désactive une connexion entière (ex. "MCP Catalog", 74 outils sur ce
POC), pas un outil individuel. Impossible donc de ne présenter au modèle
que les 2-3 outils utiles à une tâche donnée depuis cette interface. Pour
réduire le nombre d'outils exposés en permanence, il faut soit retirer un
serveur de `MCP_SERVERS_JSON` dans `bridge/.env.bridge` (et redémarrer le
bridge), soit filtrer les outils exposés côté bridge — non implémenté à ce
stade.

## Pour aller plus loin

Le system prompt améliore nettement la fiabilité mais reste dépendant du
modèle : rien ne garantit qu'il tienne sur une variante de la demande non
anticipée dans le prompt, ou avec un modèle moins capable. Une piste plus
robuste, non développée à ce stade, consisterait à exposer côté bridge un
outil composite unique (par exemple `import_opendata_vers_grist`) qui
exécuterait tout le pipeline serveur, ne laissant au modèle qu'un seul
appel à réussir plutôt que quatre. Voir la [feuille de route](../README.md#feuille-de-route).
