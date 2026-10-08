# Serveur MCP Grist auto-hébergé

Lance `mcp-server-grist` en Streamable HTTP, indépendamment de tout autre
composant. Utile si aucun serveur MCP Grist n'est déjà fourni par
l'établissement.

Retirer ce service si un serveur Grist MCP est déjà fourni par
l'établissement — pointer directement vers son URL dans la fiche
[Connecteur Grist](../docs/connectors.md#grist).

## Démarrage

```bash
cp .env.grist.example .env.grist
chmod 600 .env.grist
```

Éditer `.env.grist` avant de démarrer : renseigner `GRIST_API_KEY`, et
vérifier `GRIST_API_URL` (par défaut `https://grist.numerique.gouv.fr/api` ;
`mcp-server-grist` pointe sinon vers le SaaS public GetGrist, pas vers La
Suite numérique).

```bash
docker compose up -d
```

## Où c'est joignable

- `http://127.0.0.1:8000/mcp` depuis le Mac hôte
- `http://grist-mcp:8000/mcp` depuis un conteneur du même réseau Docker
- `http://host.docker.internal:8000/mcp` depuis un conteneur d'un autre
  projet Docker (ex. OpenWebUI lancé séparément), le port étant publié sur
  l'hôte

Voir la fiche [Connecteur Grist](../docs/connectors.md#grist) pour la
déclaration de ce serveur comme connexion MCP dans OpenWebUI.
