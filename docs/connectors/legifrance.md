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

Le serveur est hébergé par le projet OpenLegi. Il nécessite un jeton
personnel, transmis **dans l'URL elle-même** (paramètre `?token=`), pas via
un champ d'authentification séparé :

1. Créer un compte gratuit sur [openlegi.fr](https://www.openlegi.fr/).
2. Récupérer le jeton MCP depuis le tableau de bord.
3. Conserver ce jeton comme un secret (jamais dans le dépôt, les journaux
   ou les conversations).

Dans **Panneau d'administration > Réglages > Intégrations > Serveurs
d'outils externes** d'OpenWebUI, ajouter une connexion :

| Champ | Valeur |
|---|---|
| Type | **MCP (Streamable HTTP)** |
| ID | `legifrance` |
| Nom | `Légifrance` |
| URL | `https://mcp.openlegi.fr/legifrance/mcp?token=VOTRE_TOKEN` (remplacer `VOTRE_TOKEN` par le jeton réel) |
| Authentification | Aucune |

Enregistrer, puis vérifier que les outils sont découverts.

Le même jeton donne accès à d'autres services MCP exposés depuis le même
tableau de bord OpenLegi, selon le même modèle d'URL
(`https://mcp.openlegi.fr/{service}/mcp?token=VOTRE_TOKEN`) — non
catalogués dans ce dépôt pour l'instant, mais déclarables de la même façon
si besoin :

| Service | Couverture | Chemin |
|---|---|---|
| RNE (INPI) | Annuaire des entreprises (identité, immatriculation, dirigeants) — pas les documents (statuts, bilans, actes) | `/rne/mcp` |
| BOFiP | Doctrine fiscale (Bulletin officiel des finances publiques) | `/bofip/mcp` |
| BODACC | Annonces légales et commerciales | `/bodacc/mcp` |
| EUR-Lex | Législation européenne — activation à demander auprès d'OpenLegi | `/eur-lex/mcp` (à confirmer) |
| Judilibre | Décisions de justice (Cour de cassation) — pas encore disponible | — |

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
- Si le serveur n'est pas découvert, vérifier que le jeton dans l'URL est
  correct et non expiré (tableau de bord OpenLegi).
- Un champ *liste de filtrage des noms de fonctions* laissé vide peut
  provoquer une erreur de connexion sur certaines versions d'OpenWebUI —
  voir le [guide d'installation](../installation.md).
