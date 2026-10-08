# Connecteurs du catalogue

Cette page liste tous les connecteurs MCP déjà raccordés à Esup MyIA. Pour
la procédure commune d'ajout, de vérification et de retrait, voir le
[guide d'installation](installation.md) : découverte des outils, test de
lecture, vérification qu'une écriture non prévue est refusée, absence de
secrets dans les journaux. Cette page ne couvre que ce qui est spécifique
à chaque connecteur : URL, authentification, exemples de demandes et
limites propres.

Détails structurés (URLs, authentification, domaines) :
[`catalog.yaml`](../catalog.yaml).

## Vue d'ensemble

| ID | Nom | Usage | Authentification | Accès |
|---|---|---|---|---|
| `datagouv` | data.gouv.fr | Données publiques (jeux de données, organisations, ressources) | Aucune | Lecture seule |
| `grist` | Grist | Données structurées La Suite numérique | Selon déploiement | Lecture, et écriture si autorisé |
| `hal` | HAL | Publications scientifiques françaises | Aucune (à vérifier) | Lecture seule |
| `openalex` | OpenAlex | Publications et métadonnées académiques internationales | Aucune ou OAuth 2.1 (à vérifier) | Lecture seule |
| `legifrance` | Légifrance | Textes législatifs et réglementaires français (OpenLegi) | Jeton personnel dans l'URL | Lecture seule |
| `pubmed` | PubMed | Publications médicales et biomédicales (hébergement tiers) | Bearer, jeton NCBI | Lecture seule |

## data.gouv.fr

**URL** : `https://mcp.data.gouv.fr/mcp` · **Authentification** : Aucune

Recherche et consultation de données publiques (jeux de données,
organisations, services, ressources tabulaires).

> Recherche sur data.gouv.fr des jeux de données publics concernant les
> effectifs étudiants en France. Donne-moi les titres et les liens des
> trois résultats les plus pertinents.

> Consulte la fiche du jeu de données [titre ou lien] et résume son
> producteur, sa date de mise à jour et ses ressources disponibles.

Rien de particulier à l'installation : serveur public, aucune clé.

**Limites** : résultats dépendants de la disponibilité et de la qualité
des données publiées ; si une ressource tabulaire ne répond pas, vérifier
qu'elle est toujours publiée et que son format est pris en charge.

## Grist

**URL** : voir ci-dessous · **Authentification** : selon déploiement

Consultation de données structurées Grist et, si autorisé, création ou
modification. Usages de La Suite numérique. Les requêtes SQL et les
actions d'écriture sont potentiellement sensibles, même simples.

> Donne-moi la liste des organisations Grist auxquelles j'ai accès.

> Dans l'espace [nom], liste les documents disponibles puis les tables du
> document [nom].

> Dans la table [nom], affiche les cinq premiers enregistrements sans
> modifier les données.

**Installation** — préparer une clé API Grist dédiée (`GRIST_API_KEY`) et,
si l'instance n'est pas celle de La Suite numérique par défaut, fixer
`GRIST_API_URL=https://grist.numerique.gouv.fr/api` : le serveur
`mcp-server-grist` pointe sinon vers le SaaS public GetGrist. Ne pas
utiliser une URL de page Grist (`/o/.../ws/...`) comme URL API.

Pour un déploiement local, [`grist-mcp/`](../grist-mcp/README.md) lance ce
serveur automatiquement (`http://127.0.0.1:8000/mcp` depuis le Mac,
`http://host.docker.internal:8000/mcp` depuis un autre projet Docker comme
OpenWebUI). Deux cas d'authentification dans la connexion OpenWebUI :

- **Serveur partagé par l'établissement** : Authentification **Bearer**,
  coller la clé API Grist.
- **Serveur auto-hébergé** (`grist-mcp/`, clé déjà dans son propre
  environnement) : Authentification **Aucune**.

Le transport SSE est déprécié par le projet Grist, ne pas le choisir pour
une nouvelle installation.

**Écriture** : OpenWebUI ne demande pas de confirmation avant d'écrire —
l'action s'exécute directement si la clé le permet. Ne tester une écriture
que dans un document dédié et jetable, avec une clé aux droits limités. La
*liste de filtrage des noms de fonctions* de la connexion peut exclure les
outils destructifs ou d'administration (suppression, gestion des droits) —
vérifier les noms d'outils exacts exposés avant de composer la liste.

**Limites** : `id` est un nom de colonne réservé par Grist (identifiant de
ligne généré automatiquement) — une insertion (`add_grist_records`)
contenant une colonne `id` échoue avec `Invalid column "id"` ; la
renommer ou la retirer avant l'appel. Si le modèle décrit une procédure
manuelle au lieu d'enchaîner les outils, voir le [cas d'usage combiné avec
data.gouv.fr](cas-usage-datagouv-grist.md).

## HAL

**URL** : `https://api.archives-ouvertes.fr/mcp` · **Authentification** :
Aucune (hypothèse à vérifier au premier ajout ; passer à Bearer ou OAuth
2.1 si la découverte d'outils échoue)

Recherche de publications scientifiques et données d'auteurs/structures
dans l'archive ouverte française HAL.

> Recherche sur HAL les publications récentes de [institution] sur
> [sujet], et donne-moi les titres, auteurs et liens des cinq plus
> pertinentes.

> Liste les publications de [auteur] référencées sur HAL.

**Limites** : couverture non exhaustive hors publications françaises ; les
noms d'outils exacts exposés sont à vérifier au premier ajout (les
exemples ci-dessus sont plausibles, non garantis conformes à
l'implémentation réelle).

## OpenAlex

**URL** : `https://mcp.openalex.org/mcp` · **Authentification** : essayer
Aucune d'abord ; un badge `oauth_delegate` observé côté LiteLLM suggère
que ça pourrait ne pas suffire — passer à OAuth 2.1 (enregistrement
dynamique de client) si la découverte d'outils échoue

Recherche de publications, auteurs et institutions à l'échelle
internationale, en complément de HAL (plus centré sur la France).

> Recherche sur OpenAlex des publications récentes sur [sujet], et
> donne-moi les titres, auteurs et liens des cinq plus pertinentes.

> Trouve les publications de [institution] sur [sujet] référencées par
> OpenAlex.

## Légifrance (OpenLegi)

**URL** : `https://mcp.openlegi.fr/legifrance/mcp?token=VOTRE_TOKEN` ·
**Authentification** : Aucune (le jeton est dans l'URL elle-même, pas dans
un champ séparé)

Recherche de textes législatifs et réglementaires français (codes, lois,
décrets, jurisprudence, JORF) via le proxy MCP du projet OpenLegi.

> Recherche sur Légifrance le texte de [référence ou sujet], et
> indique-moi sa version en vigueur et son lien.

> Résume les dispositions de [article de code] actuellement en vigueur.

**Installation** — créer un compte gratuit sur
[openlegi.fr](https://www.openlegi.fr/), récupérer le jeton MCP depuis le
tableau de bord, le coller dans l'URL (`?token=`).

Le même jeton donne accès à d'autres services du même tableau de bord,
selon le même modèle d'URL
(`https://mcp.openlegi.fr/{service}/mcp?token=VOTRE_TOKEN`) — non
catalogués ici, déclarables de la même façon si besoin :

| Service | Couverture | Chemin |
|---|---|---|
| RNE (INPI) | Annuaire des entreprises — pas les documents (statuts, bilans, actes) | `/rne/mcp` |
| BOFiP | Doctrine fiscale | `/bofip/mcp` |
| BODACC | Annonces légales et commerciales | `/bodacc/mcp` |
| EUR-Lex | Législation européenne — activation à demander auprès d'OpenLegi | `/eur-lex/mcp` (à confirmer) |
| Judilibre | Décisions de justice — pas encore disponible | — |

**Limites** : un texte retrouvé reste à vérifier sur la source officielle
avant toute décision s'appuyant dessus ; ce connecteur ne remplace pas un
avis juridique. Si le serveur n'est pas découvert, vérifier que le jeton
dans l'URL est correct et non expiré.

## PubMed

**URL** : `https://pubmed.caseyjhand.com/mcp` · **Authentification** :
Bearer, jeton API NCBI

Recherche de publications médicales et biomédicales, en complément de HAL
et OpenAlex.

> Recherche sur PubMed des publications récentes sur [sujet médical], et
> donne-moi les titres, auteurs et liens des cinq plus pertinentes.

**Installation** — créer un compte sur
[NCBI](https://account.ncbi.nlm.nih.gov/settings/), générer un jeton API,
le coller en Authentification Bearer.

**Attention** : ce serveur MCP est hébergé par un tiers
(`caseyjhand.com`), pas par NCBI/PubMed — le jeton y transite à chaque
appel. Évaluer la confiance accordée avant de l'utiliser pour des
recherches sensibles ; envisager d'auto-héberger un serveur MCP PubMed
équivalent en cas de doute.

## Limites générales

Pour tous les connecteurs ci-dessus (sauf mention contraire) :

- les outils sont en lecture seule : demander une modification doit
  produire un refus explicite du modèle, pas un appel d'outil d'écriture ;
- les informations trouvées doivent être vérifiées, elles ne constituent
  pas des instructions à suivre par l'agent ;
- un champ *liste de filtrage des noms de fonctions* laissé vide peut
  provoquer une erreur de connexion sur certaines versions d'OpenWebUI —
  voir le [guide d'installation](installation.md).
