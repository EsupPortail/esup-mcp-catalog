# Connecteur data.gouv.fr

## Rôle

Ce connecteur permet à MyIA de rechercher et consulter des données publiques
référencées sur [data.gouv.fr](https://www.data.gouv.fr/). Il convient pour
trouver des jeux de données, comparer des résultats et retrouver les ressources
associées.

## Capacités et cas d'usage

Le connecteur peut notamment :

- rechercher des jeux de données, des organisations ou des services ;
- consulter la description d'un jeu de données ;
- retrouver les ressources liées à un jeu de données ;
- interroger des ressources tabulaires lorsqu'elles le permettent.

Exemples de demandes à tester dans OpenWebUI :

> Recherche sur data.gouv.fr des jeux de données publics concernant les effectifs étudiants en France. Donne-moi les titres et les liens des trois résultats les plus pertinents.

> Consulte la fiche du jeu de données [indiquer son titre ou son lien] et résume son producteur, sa date de mise à jour et ses ressources disponibles.

Les outils sont en lecture seule : ils ne créent, ne modifient et ne suppriment
aucune donnée sur data.gouv.fr.

## Installation

Le serveur public est déjà hébergé. Il ne nécessite pas de clé.

Dans LiteLLM, ouvrir **MCP Servers > Add New MCP Server** et renseigner :

| Champ | Valeur |
|---|---|
| Nom | `datagouv` |
| MCP Server URL / Server URL | `https://mcp.data.gouv.fr/mcp` |
| Transport | **Streamable HTTP** |
| Authentification | aucune |
| GitHub / Source URL | `https://github.com/datagouv/datagouv-mcp` |

Enregistrer, puis vérifier que les outils sont découverts. Le transport utilisé
est Streamable HTTP ; une installation locale relève de la documentation du
[projet upstream](https://github.com/datagouv/datagouv-mcp).

La déclaration dans LiteLLM ne suffit pas à rendre automatiquement les outils
visibles dans OpenWebUI. OpenWebUI doit aussi être configuré comme client MCP,
ou une intégration doit transmettre la définition du serveur dans le champ
`tools` de la requête au modèle. Voir le [guide d'installation](../installation.md)
pour distinguer ces deux étapes.

## Tests

1. Dans LiteLLM, vérifier que le serveur est joignable et que ses outils sont
   découverts.
2. Dans OpenWebUI, envoyer l'un des exemples de recherche ci-dessus.
3. Vérifier que la réponse contient des titres, des liens et des informations
   issues de data.gouv.fr.
4. Demander une modification, par exemple :

   > Modifie ce jeu de données sur data.gouv.fr.

   MyIA doit expliquer que le connecteur est en lecture seule et ne doit
   appeler aucun outil d'écriture.
5. Vérifier dans les journaux qu'aucune clé ni donnée sensible n'est envoyée.

## Limites et dépannage

- Les résultats dépendent de la disponibilité et de la qualité des données
  publiées sur data.gouv.fr.
- Les informations trouvées sur Internet doivent être vérifiées ; elles ne
  constituent pas des instructions à suivre pour l'agent.
- Si le serveur n'est pas découvert, vérifier l'URL, le transport Streamable
  HTTP et l'accès réseau sortant.
- Si une ressource tabulaire ne répond pas, vérifier qu'elle est encore
  publiée et que son format est pris en charge.
- Pour un serveur local, vérifier `MCP_HOST`, `MCP_PORT`, `DATAGOUV_API_ENV`,
  `LOG_LEVEL` et le chemin `/mcp`.