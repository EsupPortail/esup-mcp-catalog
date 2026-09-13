# Bridge MCP vers OpenAPI

Ce service expose les outils MCP sous forme d'operations OpenAPI utilisables
par OpenWebUI. Il decouvre les outils au demarrage et relaie les appels vers
les serveurs MCP configures dans `MCP_SERVERS_JSON`.

Le bridge lit sa propre configuration et ne recopie pas automatiquement les
serveurs enregistres dans la base LiteLLM. LiteLLM reste la passerelle du modele
utilise par OpenWebUI ; le bridge est la passerelle des outils dans ce scenario.

## Demarrage

Depuis ce repertoire :

```bash
cp .env.bridge.example .env.bridge
chmod 600 .env.bridge
docker compose up -d
```

Ne committez jamais `.env.bridge`. La cle `BRIDGE_API_KEY` protege les appels
aux outils.

## Connexion OpenWebUI

Dans **Admin > Settings > Tools > Add connection** :

| Champ | Valeur |
|---|---|
| Type | OpenAPI |
| Nom d'utilisateur | `MCP Catalog` |
| URL | `http://host.docker.internal:8090` |
| Auth | Bearer |
| Cle API | la valeur de `BRIDGE_API_KEY` |

Depuis un OpenWebUI lance dans Docker Desktop, `host.docker.internal` designe
le Mac hote. Si OpenWebUI et le bridge sont places sur le meme reseau Docker,
utilisez plutot `http://mcp-openapi-bridge:8090`.

Ne pas ajouter `/openapi.json` a la fin de l'URL : OpenWebUI l'ajoute lui-meme.
Le mettre quand meme produit une requete vers `.../openapi.json/openapi.json`,
qui echoue en 404.

## Configuration MCP

Le bridge accepte les serveurs Streamable HTTP. Exemple :

```json
{
  "datagouv": {
    "transport": "streamable-http",
    "url": "https://mcp.data.gouv.fr/mcp"
  },
  "grist": {
    "transport": "streamable-http",
    "url": "http://host.docker.internal:8000/mcp"
  }
}
```

Les URL et les outils sont interroges au demarrage. Redemarrez le bridge apres
chaque modification de `.env.bridge`.

Le bridge ne stocke pas les cles des services dans le depot. Les droits
restent ceux du serveur MCP cible ; commencez par des serveurs en lecture seule.
