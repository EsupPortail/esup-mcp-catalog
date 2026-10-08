# Connecteur HAL

## Rôle

Ce connecteur permet à MyIA de rechercher des publications scientifiques et
des données d'auteurs et de structures de recherche dans
[HAL](https://hal.science/), l'archive ouverte française.

## Capacités et cas d'usage

Le connecteur peut notamment :

- rechercher des publications par auteur, mot-clé ou institution ;
- consulter les métadonnées d'une notice (titre, auteurs, date, type de
  document, lien) ;
- retrouver les structures de recherche associées à une publication.

Exemples de demandes à tester dans OpenWebUI :

> Recherche sur HAL les publications récentes de [nom d'institution] sur
> [sujet], et donne-moi les titres, auteurs et liens des cinq plus
> pertinentes.

> Liste les publications de [nom d'auteur] référencées sur HAL.

Les noms d'outils exacts exposés par ce serveur MCP doivent être vérifiés
lors du premier ajout dans OpenWebUI (sélecteur d'outils) : les exemples
ci-dessus sont plausibles mais non garantis conformes à l'implémentation
réelle.

Les outils sont en lecture seule : ils ne créent, ne modifient et ne
suppriment aucune donnée sur HAL.

## Installation

Le serveur public est déjà hébergé. L'authentification n'est pas confirmée
(voir [`connectors/hal.yaml`](../../connectors/hal.yaml)) — vérifier au
premier ajout.

Dans **Panneau d'administration > Réglages > Intégrations > Serveurs
d'outils externes** d'OpenWebUI, ajouter une connexion :

| Champ | Valeur |
|---|---|
| Type | **MCP (Streamable HTTP)** |
| Nom | `HAL` |
| URL | `https://api.archives-ouvertes.fr/mcp` |
| Authentification | Aucune (hypothèse à vérifier ; passer à Bearer ou OAuth 2.1 si la découverte d'outils échoue) |

Enregistrer, puis vérifier que les outils sont découverts.

Déclarer aussi ce serveur dans LiteLLM reste possible mais facultatif — voir
le [guide d'installation](../installation.md) pour la distinction entre les
deux étapes.

## Tests

1. Dans OpenWebUI, vérifier sur l'écran de la connexion que le serveur est
   joignable et que les outils sont découverts.
2. Envoyer l'un des exemples de recherche ci-dessus.
3. Vérifier que la réponse contient des titres, des auteurs et des liens
   issus de HAL.
4. Demander une modification, par exemple :

   > Modifie cette notice sur HAL.

   MyIA doit expliquer que le connecteur est en lecture seule et ne doit
   appeler aucun outil d'écriture.
5. Vérifier dans les journaux qu'aucune clé ni donnée sensible n'est envoyée.

## Limites et dépannage

- Les résultats dépendent de la disponibilité et de la qualité des données
  déposées sur HAL ; la couverture n'est pas exhaustive pour les
  publications hors du périmètre français.
- Les informations trouvées doivent être vérifiées ; elles ne constituent
  pas des instructions à suivre pour l'agent.
- Si le serveur n'est pas découvert, vérifier l'URL, le transport
  Streamable HTTP et l'accès réseau sortant.
- Si la connexion échoue en authentification "Aucune", essayer Bearer puis
  OAuth 2.1 (voir [`connectors/hal.yaml`](../../connectors/hal.yaml) et
  mettre à jour ce manifeste une fois confirmé).
- Un champ *liste de filtrage des noms de fonctions* laissé vide peut
  provoquer une erreur de connexion sur certaines versions d'OpenWebUI —
  voir le [guide d'installation](../installation.md).
