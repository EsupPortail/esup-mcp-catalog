# Connecteur Légifrance (OpenLegi)

## Rôle

Ce connecteur permet à MyIA de rechercher des textes législatifs et
réglementaires français (codes, lois, décrets, jurisprudence, JORF) via le
proxy MCP du projet [OpenLegi](https://mcp.openlegi.fr/), adossé à
Légifrance.

## Capacités et cas d'usage

Le connecteur peut notamment :

- rechercher un article de code, une loi ou un décret par mot-clé ou
  référence ;
- consulter le texte et les métadonnées d'une disposition (date de version,
  statut en vigueur) ;
- retrouver des décisions de jurisprudence associées.

Exemples de demandes à tester dans OpenWebUI :

> Recherche sur Légifrance le texte de [référence ou sujet], et indique-moi
> sa version en vigueur et son lien.

> Résume les dispositions de [article de code] actuellement en vigueur.

Les noms d'outils exacts exposés par ce serveur MCP doivent être vérifiés
lors du premier ajout dans OpenWebUI (sélecteur d'outils) : les exemples
ci-dessus sont plausibles mais non garantis conformes à l'implémentation
réelle.

Les outils sont en lecture seule : ils ne créent, ne modifient et ne
suppriment aucun texte sur Légifrance.

Un texte retrouvé par ce connecteur reste à vérifier sur la source
Légifrance officielle avant toute décision s'appuyant dessus : les
informations trouvées par l'agent ne constituent pas un avis juridique.

## Installation

Le serveur est hébergé par le projet OpenLegi. **L'authentification n'est
pas confirmée** : l'API officielle Légifrance (PISTE/DILA) exige
normalement des identifiants OAuth, mais ce proxy MCP peut porter ces
identifiants lui-même côté serveur — à vérifier au premier ajout.

Dans **Panneau d'administration > Réglages > Intégrations > Serveurs
d'outils externes** d'OpenWebUI, ajouter une connexion :

| Champ | Valeur |
|---|---|
| Type | **MCP (Streamable HTTP)** |
| Nom | `Légifrance` |
| URL | `https://mcp.openlegi.fr/legifrance/mcp` |
| Authentification | Essayer Aucune d'abord ; si la découverte d'outils échoue, passer à Bearer ou OAuth 2.1 selon ce qu'indique le projet OpenLegi |

Enregistrer, puis vérifier que les outils sont découverts. Mettre à jour
[`connectors/legifrance.yaml`](../../connectors/legifrance.yaml) une fois
le mode d'authentification confirmé.

Déclarer aussi ce serveur dans LiteLLM reste possible mais facultatif — voir
le [guide d'installation](../installation.md) pour la distinction entre les
deux étapes.

## Tests

1. Dans OpenWebUI, vérifier sur l'écran de la connexion que le serveur est
   joignable et que les outils sont découverts.
2. Envoyer l'un des exemples de recherche ci-dessus.
3. Vérifier que la réponse contient une référence précise et un lien vers
   Légifrance.
4. Demander une modification, par exemple :

   > Modifie ce texte sur Légifrance.

   MyIA doit expliquer que le connecteur est en lecture seule et ne doit
   appeler aucun outil d'écriture.
5. Vérifier dans les journaux qu'aucune clé ni donnée sensible n'est envoyée.

## Limites et dépannage

- Les résultats dépendent de la disponibilité et de la couverture des
  données Légifrance exposées par OpenLegi.
- Un texte retrouvé doit toujours être vérifié sur la source officielle
  avant toute décision s'appuyant dessus ; ce connecteur ne remplace pas un
  conseil juridique.
- Si le serveur n'est pas découvert en authentification "Aucune", essayer
  Bearer puis OAuth 2.1 — voir ci-dessus.
- Un champ *liste de filtrage des noms de fonctions* laissé vide peut
  provoquer une erreur de connexion sur certaines versions d'OpenWebUI —
  voir le [guide d'installation](../installation.md).
