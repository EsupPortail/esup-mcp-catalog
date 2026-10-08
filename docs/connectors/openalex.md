# Connecteur OpenAlex

## Rôle

Ce connecteur permet à MyIA de rechercher des publications, auteurs et
institutions référencés par [OpenAlex](https://docs.openalex.org/), à
l'échelle internationale — en complément du connecteur [HAL](hal.md), plus
centré sur les publications françaises.

## Capacités et cas d'usage

Le connecteur peut notamment :

- rechercher des publications (*works*) par mot-clé, auteur ou institution ;
- consulter les métadonnées d'une publication (auteurs, date, citations,
  accès libre) ;
- retrouver les institutions et revues associées.

Exemples de demandes à tester dans OpenWebUI :

> Recherche sur OpenAlex des publications récentes sur [sujet], et
> donne-moi les titres, auteurs et liens des cinq plus pertinentes.

> Trouve les publications de [nom d'institution] sur [sujet] référencées
> par OpenAlex.

Les noms d'outils exacts exposés par ce serveur MCP doivent être vérifiés
lors du premier ajout dans OpenWebUI (sélecteur d'outils) : les exemples
ci-dessus sont plausibles mais non garantis conformes à l'implémentation
réelle.

Les outils sont en lecture seule : ils ne créent, ne modifient et ne
suppriment aucune donnée sur OpenAlex.

## Installation

Le serveur public est déjà hébergé. **L'authentification n'est pas
confirmée** pour ce connecteur plus que pour les autres : un badge
`oauth_delegate` a été observé côté LiteLLM, ce qui suggère que
l'authentification "Aucune" pourrait ne pas suffire malgré le caractère
public de l'API OpenAlex sous-jacente — à vérifier en premier lors de
l'ajout.

Dans **Panneau d'administration > Réglages > Intégrations > Serveurs
d'outils externes** d'OpenWebUI, ajouter une connexion :

| Champ | Valeur |
|---|---|
| Type | **MCP (Streamable HTTP)** |
| Nom | `OpenAlex` |
| URL | `https://mcp.openalex.org/mcp` |
| Authentification | Essayer Aucune d'abord ; si la découverte d'outils échoue, passer à OAuth 2.1 (enregistrement dynamique de client) |

Enregistrer, puis vérifier que les outils sont découverts. Mettre à jour
[`connectors/openalex.yaml`](../../connectors/openalex.yaml) une fois le
mode d'authentification confirmé.

Déclarer aussi ce serveur dans LiteLLM reste possible mais facultatif — voir
le [guide d'installation](../installation.md).

## Tests

1. Dans OpenWebUI, vérifier sur l'écran de la connexion que le serveur est
   joignable et que les outils sont découverts.
2. Envoyer l'un des exemples de recherche ci-dessus.
3. Vérifier que la réponse contient des titres, des auteurs et des liens
   issus d'OpenAlex.
4. Demander une modification, par exemple :

   > Modifie cette notice sur OpenAlex.

   MyIA doit expliquer que le connecteur est en lecture seule et ne doit
   appeler aucun outil d'écriture.
5. Vérifier dans les journaux qu'aucune clé ni donnée sensible n'est envoyée.

## Limites et dépannage

- Les résultats dépendent de la disponibilité et de la qualité des
  métadonnées référencées par OpenAlex.
- Les informations trouvées doivent être vérifiées ; elles ne constituent
  pas des instructions à suivre pour l'agent.
- Si le serveur n'est pas découvert en authentification "Aucune", passer à
  OAuth 2.1 — voir ci-dessus.
- Un champ *liste de filtrage des noms de fonctions* laissé vide peut
  provoquer une erreur de connexion sur certaines versions d'OpenWebUI —
  voir le [guide d'installation](../installation.md).
