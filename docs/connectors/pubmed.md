# Connecteur PubMed

## Rôle

Ce connecteur permet à MyIA de rechercher des publications médicales et
biomédicales référencées sur [PubMed](https://pubmed.ncbi.nlm.nih.gov/)
(NCBI), en complément des connecteurs académiques généralistes
[HAL](hal.md) et [OpenAlex](openalex.md).

## Capacités et cas d'usage

Le connecteur peut notamment :

- rechercher des publications par mot-clé, auteur ou revue ;
- consulter les métadonnées d'une publication (titre, auteurs, revue,
  date, résumé, identifiants).

Exemples de demandes à tester dans OpenWebUI :

> Recherche sur PubMed des publications récentes sur [sujet médical], et
> donne-moi les titres, auteurs et liens des cinq plus pertinentes.

Les noms d'outils exacts exposés par ce serveur MCP doivent être vérifiés
lors du premier ajout dans OpenWebUI (sélecteur d'outils) : l'exemple
ci-dessus est plausible mais non garanti conforme à l'implémentation
réelle.

Les outils sont en lecture seule : ils ne créent, ne modifient et ne
suppriment aucune donnée sur PubMed.

## Installation

Ce serveur MCP est hébergé par un tiers (`caseyjhand.com`), **pas par
NCBI/PubMed lui-même**. Il nécessite un jeton API NCBI, qui transite par
cet hébergeur tiers à chaque appel — évaluer la confiance accordée avant
de l'utiliser pour des recherches sensibles.

1. Créer un compte sur [NCBI](https://account.ncbi.nlm.nih.gov/settings/).
2. Générer un jeton API depuis les réglages du compte.
3. Conserver ce jeton comme un secret (jamais dans le dépôt, les journaux
   ou les conversations).

Dans **Panneau d'administration > Réglages > Intégrations > Serveurs
d'outils externes** d'OpenWebUI, ajouter une connexion :

| Champ | Valeur |
|---|---|
| Type | **MCP (Streamable HTTP)** |
| ID | `pubmed` |
| Nom | `PubMed` |
| URL | `https://pubmed.caseyjhand.com/mcp` |
| Authentification | Bearer — coller le jeton API NCBI dans le champ secret |

Enregistrer, puis vérifier que les outils sont découverts.

Déclarer aussi ce serveur dans LiteLLM reste possible mais facultatif — voir
le [guide d'installation](../installation.md) pour la distinction entre les
deux étapes.

## Tests

1. Dans OpenWebUI, vérifier sur l'écran de la connexion que le serveur est
   joignable et que les outils sont découverts.
2. Envoyer l'exemple de recherche ci-dessus.
3. Vérifier que la réponse contient des titres, des auteurs et des liens
   issus de PubMed.
4. Demander une modification, par exemple :

   > Modifie cette notice sur PubMed.

   MyIA doit expliquer que le connecteur est en lecture seule et ne doit
   appeler aucun outil d'écriture.
5. Vérifier dans les journaux qu'aucune clé ni donnée sensible n'est envoyée.

## Limites et dépannage

- Ce serveur est hébergé par un tiers, pas par NCBI : en cas de doute sur
  la confiance à lui accorder, envisager d'auto-héberger un serveur MCP
  PubMed équivalent plutôt que de lui transmettre un jeton NCBI personnel.
- Les résultats dépendent de la disponibilité et de la couverture de
  PubMed ; les informations trouvées doivent être vérifiées avant toute
  décision s'appuyant dessus.
- Si le serveur n'est pas découvert, vérifier que le jeton NCBI est
  valide et correctement collé dans le champ Bearer.
- Un champ *liste de filtrage des noms de fonctions* laissé vide peut
  provoquer une erreur de connexion sur certaines versions d'OpenWebUI —
  voir le [guide d'installation](../installation.md).
