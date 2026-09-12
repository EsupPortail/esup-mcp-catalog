# Connecteur data.gouv.fr

## Rôle

Ce connecteur permet à MyIA de rechercher et consulter des données publiques référencées sur data.gouv.fr. Il est adapté aux questions de découverte, de comparaison et de synthèse de données ouvertes.

## Source et accès

- Dépôt : [datagouv/datagouv-mcp](https://github.com/datagouv/datagouv-mcp)
- Instance publique : `https://mcp.data.gouv.fr/mcp`
- Échange : Streamable HTTP
- Clé d'accès : aucune pour l'instance publique

Le projet upstream indique que le serveur utilise uniquement le transport Streamable HTTP. Une installation locale peut être configurée avec `MCP_HOST`, `MCP_PORT`, `DATAGOUV_API_ENV` et `LOG_LEVEL`.

## Capacités

Le serveur permet notamment de :

- rechercher des jeux de données et des organisations ;
- rechercher des services de données référencés ;
- consulter les informations d'un jeu de données ou d'une ressource ;
- interroger des ressources tabulaires ;
- consulter des métriques lorsqu'elles sont disponibles.

Les outils sont en lecture seule. Ils ne créent ni ne modifient de données sur data.gouv.fr.

## Intégration MyIA

Pour un client MCP HTTP, l'URL à déclarer est :

```json
{
  "url": "https://mcp.data.gouv.fr/mcp",
  "type": "http"
}
```

Dans MyIA, l'accès doit rester limité aux outils de lecture. Les réponses provenant de données publiques ou de services référencés sont des informations à vérifier ; elles ne doivent pas être traitées comme des instructions par l'agent.

## Test initial

1. Déclarer l'URL publique dans le client MCP.
2. Vérifier que les outils sont découverts.
3. Tester une recherche simple de jeu de données.
4. Vérifier qu'aucune clé ou donnée sensible n'est ajoutée à la configuration.

## Limites et dépannage

- L'instance publique dépend de la disponibilité du service data.gouv.fr.
- La qualité des résultats dépend des jeux de données et services référencés.
- Pour un serveur local, vérifier `MCP_HOST`, `MCP_PORT` et l'URL `/mcp`.
- Les métriques nécessitent l'environnement data.gouv.fr approprié.
