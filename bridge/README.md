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
```

Editer `.env.bridge` avant de demarrer :

- remplacer `BRIDGE_API_KEY` par une valeur generee avec
  `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` ;
- ajuster `MCP_SERVERS_JSON` pour ne garder que les serveurs MCP reellement
  utilises.

Puis demarrer :

```bash
docker compose up -d
```

Ne committez jamais `.env.bridge`. La cle `BRIDGE_API_KEY` protege les appels
aux outils.

## Connexion OpenWebUI

Le selecteur d'outils d'OpenWebUI (icone dans la fenetre de conversation)
active ou desactive une connexion entiere, pas un outil individuel. Declarer
**une connexion par serveur MCP**, plutot qu'une seule connexion regroupant
tout, pour pouvoir choisir au cas par cas quel connecteur utiliser sans
noyer le modele sous des outils sans rapport avec la demande.

Dans **Panneau d'administration > Réglages > Intégrations > Gérer les
serveurs d'outils** (nommé *Tools > Add connection* dans les versions plus
anciennes d'OpenWebUI), ajouter une connexion par serveur configure dans
`MCP_SERVERS_JSON`, par exemple pour `datagouv` :

| Champ | Valeur |
|---|---|
| Type | OpenAPI |
| Nom d'utilisateur | `data.gouv.fr` |
| URL | `http://host.docker.internal:8090/servers/datagouv` |
| Auth | Bearer |
| Cle API | la valeur de `BRIDGE_API_KEY` |

Repeter pour chaque serveur (`grist`, etc.), en changeant le nom et le
`{nom}` a la fin de l'URL pour qu'il corresponde a la cle utilisee dans
`MCP_SERVERS_JSON`.

Le champ "Nom d'utilisateur" est un intitule trompeur d'OpenWebUI (chaine
generique reutilisee sur ce formulaire) : c'est en realite le nom de la
connexion, pas un identifiant de compte. Le laisser vide produit une
connexion sans nom affiche dans le selecteur d'outils (juste une icone) ;
toujours y mettre un nom descriptif.

Depuis un OpenWebUI lance dans Docker Desktop, `host.docker.internal` designe
le Mac hote. Si OpenWebUI et le bridge sont places sur le meme reseau Docker,
utilisez plutot `http://mcp-openapi-bridge:8090/servers/{nom}`.

Ne pas ajouter `/openapi.json` a la fin de l'URL : OpenWebUI l'ajoute lui-meme.
Le mettre quand meme produit une requete vers `.../openapi.json/openapi.json`,
qui echoue en 404.

Apres avoir ajoute ou modifie une connexion, faire un **rechargement complet**
de la page (Cmd/Ctrl+Maj+R, pas juste F5) avant de verifier le selecteur
d'outils dans une conversation : OpenWebUI garde la liste des connexions en
cache cote navigateur et peut continuer d'afficher l'ancien etat sinon,
donnant l'impression qu'une connexion pourtant bien enregistree n'existe
pas.

La connexion generale `http://host.docker.internal:8090` (tous les serveurs
en une seule fois, sans le prefixe `/servers/{nom}`) reste disponible mais
n'est pas recommandee en complement des connexions par serveur : les memes
outils apparaitraient alors deux fois dans le selecteur.

Le bridge n'envoie pas d'en-tetes CORS restrictifs (`Access-Control-Allow-
Origin: *` sur les routes de decouverte) : l'ecran Integrations d'OpenWebUI
verifie une connexion depuis le navigateur, pas depuis son propre backend,
et bloquerait sinon l'enregistrement meme quand le bridge est parfaitement
joignable.

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
    "url": "http://grist-mcp:8000/mcp"
  }
}
```

Les URL et les outils sont interroges au demarrage. Redemarrez le bridge apres
chaque modification de `.env.bridge`.

Si un serveur MCP redemarre pendant que le bridge tourne, sa session
devient invalide cote bridge. Le premier appel suivant echoue (502), le
bridge se reconnecte automatiquement, et l'appel suivant fonctionne sans
intervention manuelle.

Le bridge ne stocke pas les cles des services dans le depot. Les droits
restent ceux du serveur MCP cible ; commencez par des serveurs en lecture seule.

## Serveur MCP Grist auto-heberge (optionnel)

Le `docker-compose.yml` inclut un service `grist-mcp` qui lance
`mcp-server-grist` en Streamable HTTP, joignable par le bridge sous
`http://grist-mcp:8000/mcp`. Son port est aussi publie sur l'hote
(`http://host.docker.internal:8000/mcp`) pour qu'un autre service, comme
LiteLLM, puisse s'y connecter.

```bash
cp .env.grist.example .env.grist
chmod 600 .env.grist
# renseigner GRIST_API_KEY dans .env.grist
docker compose up -d
```

Retirer le service `grist-mcp` du `docker-compose.yml` si un serveur MCP
Grist est deja fourni par l'etablissement.
