# MCP Catalog pour Esup MyIA

Ce dépôt constitue le POC du catalogue de serveurs MCP pour Esup MyIA. Il documente le raccordement d'Esup MyIA Mistral AMUE à deux serveurs MCP existants :

- [data.gouv.fr MCP](https://github.com/datagouv/datagouv-mcp), serveur public de consultation des données et ressources data.gouv.fr ;
- [Grist MCP](https://github.com/nic01asFr/mcp-server-grist), connecteur Grist utilisé pour les besoins de La Suite numérique.

Le code de ces serveurs reste externe à ce dépôt.

## Projet communautaire

Ce POC s'inscrit dans un projet de magasin mutualisé de serveurs MCP pour l'ESR/Esup, adossé à `esup-myia-mistral-amue`. L'objectif est d'éviter que chaque établissement réimplémente les mêmes connecteurs et de permettre à un assistant IA souverain d'agir dans les outils métiers de son écosystème.

Un serveur MCP est la couche d'intégration qui transforme une API existante en outils utilisables par un agent en langage naturel. À terme, le même catalogue pourra servir MyIA/OpenWebUI et d'autres clients MCP, avec des scénarios composés entre plusieurs applications. Chaque établissement restera maître des connecteurs qu'il active, des comptes de service utilisés et des autorisations accordées.

Le projet vise des composants open source et souverains de l'ESR, de La Suite numérique et des communs numériques de l'État. Le catalogue doit privilégier les applications disposant d'une API mature et d'une valeur d'usage claire, tout en écartant les intégrations dont le risque ou la sensibilité est disproportionné.

## Comment lire ce document

Ce document s'adresse d'abord aux personnes qui connaissent les usages de MyIA et les applications de l'ESR, sans nécessairement développer des logiciels. Les exemples techniques servent à montrer comment un connecteur est installé et protégé ; ils ne sont pas nécessaires pour comprendre le projet. Les mots spécialisés sont définis dans le [glossaire](#glossaire).

## Architecture

```mermaid
flowchart LR
    U[Utilisateur] --> OW[OpenWebUI]
    OW --> AB[Esup MCP Agent Bridge]
    AB --> LL[LiteLLM]
    LL --> M[Mistral ESR / ILaaS]
    AB --> DG[data.gouv.fr MCP]
    AB --> GR[Grist MCP / La Suite]
    AB --> A[Autorisations, confirmations et audit]
```

Le bridge conserve les règles d'accès, les confirmations humaines et l'audit. Les secrets ne doivent jamais être envoyés à OpenWebUI, au modèle, dans les logs ou dans Git.

## Serveurs MCP du POC

Le POC propose deux connecteurs :

| Connecteur | Usage principal | Accès |
|---|---|---|
| data.gouv.fr | Rechercher et consulter des données publiques | Serveur public, lecture seule |
| Grist / La Suite numérique | Consulter des données structurées et, si autorisé, les modifier | Instance Grist de l'établissement, clé dédiée |

Les procédures, exemples de demandes, paramètres LiteLLM, tests et limites sont
regroupés dans les fiches dédiées :

- [Connecteur data.gouv.fr](docs/connectors/datagouv.md) ;
- [Connecteur Grist](docs/connectors/grist.md).

Le [guide d'installation](docs/installation.md) décrit le parcours commun dans
LiteLLM et OpenWebUI. Les secrets ne doivent jamais être inscrits dans ce
dépôt.

## Documentation des connecteurs

Le parcours commun d'ajout, de test et de retrait est décrit dans le [guide
d'installation](docs/installation.md). Les fiches liées ci-dessus portent les
réglages et les exemples propres à chaque connecteur.

Le catalogue et les manifestes YAML associés sont disponibles ici :

- [Catalogue du POC](catalog.yaml) ;
- [Manifeste data.gouv.fr](connectors/datagouv.yaml) ;
- [Manifeste Grist](connectors/grist.yaml).

## Périmètre et évolutions

Le POC se limite à data.gouv.fr et Grist. D'autres connecteurs pourront être étudiés ultérieurement selon la maturité de leur API, leur utilité pour l'ESR, leur maintenabilité et le niveau de risque associé.

Les applications manipulant des données sensibles nécessiteront une analyse RGPD et sécurité dédiée avant toute intégration. Les fonctions d'authentification multifacteur et les envois massifs ne font pas partie des usages visés.

Le catalogue n'est pas une liste d'intégrations disponibles : chaque connecteur devra être évalué, documenté, versionné et validé avant d'être proposé aux établissements.

## Déploiement cible

Chaque connecteur a vocation à être un conteneur Docker autonome, déclaré comme service optionnel de la stack MyIA. Son activation suit un parcours commun :

1. choisir les connecteurs utiles parmi le catalogue ;
2. déclarer l'adresse de l'application et les secrets dans la configuration locale de l'établissement ;
3. activer l'outil dans l'administration MyIA/OpenWebUI ;
4. vérifier les permissions, le healthcheck et l'audit avant ouverture aux utilisateurs.

L'utilisateur final ne configure pas les connecteurs. Le bridge et la couche d'administration portent les règles d'accès, les confirmations avant écriture et la journalisation sans contenu sensible.

## Gouvernance et maintenance

Le catalogue a vocation à être communautaire. Chaque module devra documenter ses prérequis, ses permissions, ses versions d'API et ses limites, puis faire l'objet d'une revue avant d'être recommandé. Les modules développés dans le cadre Esup suivront la licence retenue par la communauté ; les licences des serveurs et dépendances externes restent à vérifier séparément.

## Vérifications du POC

Les vérifications détaillées et les exemples de demandes sont regroupés dans
les fiches liées plus haut. Elles couvrent la découverte des outils, les
lectures de test, les confirmations avant écriture et la protection des
secrets.

## Feuille de route

- ajouter le catalogue validé au bridge ;
- définir le manifeste, le label de compatibilité et le processus de revue communautaire ;
- intégrer les permissions par utilisateur et groupe ;
- limiter les outils Grist exposés selon le profil ;
- ajouter healthchecks, timeouts, limites de résultats et audit ;
- tester la configuration Docker et les connexions MCP sans secret réel ;
- évaluer progressivement les candidats du catalogue selon leur API et leur niveau de risque.

## Glossaire

- **API** : interface proposée par une application pour permettre à un autre logiciel de lui demander des informations ou de lui faire effectuer une action.
- **Assistant IA** : logiciel qui comprend une demande en langage naturel et peut, lorsque cela est autorisé, utiliser des outils externes pour y répondre.
- **MCP** (*Model Context Protocol*) : protocole ouvert qui décrit la manière de présenter des outils et des données à un assistant IA.
- **Serveur MCP** : connecteur qui traduit les demandes de l'assistant en appels compréhensibles par une application, et qui renvoie les résultats à l'assistant.
- **Connecteur** : autre nom donné à un serveur MCP lorsqu'on insiste sur son rôle de liaison avec une application.
- **Bridge** : composant intermédiaire qui choisit les connecteurs utilisables, vérifie les droits et demande une confirmation avant une action sensible.
- **Endpoint** : adresse précise à laquelle un service est joignable, par exemple `https://mcp.data.gouv.fr/mcp`.
- **Transport** : manière dont le client et le serveur échangent leurs messages. `Streamable HTTP` utilise une connexion web ; `STDIO` utilise les entrées et sorties d'un programme lancé localement.
- **LiteLLM** : composant qui relaie les demandes entre MyIA et le modèle Mistral, et qui peut aussi déclarer des serveurs MCP.
- **OpenWebUI** : interface web utilisée par MyIA pour dialoguer avec l'assistant.
- **ILaaS** : service de l'AMUE donnant accès aux modèles Mistral pour l'enseignement supérieur et la recherche.
- **Secret** : information confidentielle, comme une clé d'accès, qui doit rester dans la configuration locale ou un coffre de secrets.
- **Healthcheck** : vérification automatique indiquant qu'un service répond correctement.
- **RGPD** : règlement européen qui encadre la collecte, l'utilisation et la protection des données personnelles.
- **Lecture seule** : capacité de consulter des informations sans pouvoir les créer, modifier ou supprimer.

## Références

- [Esup MyIA Mistral AMUE](https://github.com/EsupPortail/esup-myia-mistral-amue)
- [Documentation LiteLLM MCP](https://docs.litellm.ai/docs/mcp)
- [Spécification Model Context Protocol](https://modelcontextprotocol.io/)
