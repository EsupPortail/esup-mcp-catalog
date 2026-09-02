# Prototype MCP LimeSurvey

Ce guide décrit un test local du serveur MCP LimeSurvey avec MyIA, LiteLLM et Mistral ESR/ILaaS.

Le prototype LimeSurvey est fourni séparément dans `mcp-limesurvey-master.zip`. Il n'est pas intégré au catalogue GitHub par ce guide.

## 1. Prérequis

- Docker Desktop
- Python 3.13 ou supérieur
- `uv`
- une instance LimeSurvey accessible
- un compte LimeSurvey autorisé à utiliser l'API Remote Control
- une clé ILaaS/Mistral ESR

Sur macOS :

```bash
brew install uv
```

Vérifier l'environnement :

```bash
docker --version
uv --version
python3 --version
```

## 2. Démarrer MyIA et Mistral ESR

### Cas d'une instance MyIA déjà déployée

Si MyIA est déjà installé dans `/Users/nicktruch/Code/myia`, ne pas recréer la stack et ne pas toucher à ses volumes. Vérifier d'abord que Docker Desktop est démarré, puis contrôler les services depuis ce dossier :

```bash
cd /Users/nicktruch/Code/myia
docker compose -f docker-compose.macos.yml ps
curl http://127.0.0.1:4000/health/liveliness
open http://localhost:3000
```

Dans ce cas, le prototype MCP peut être lancé séparément sur l'hôte, sur le port `8001`. LiteLLM, qui tourne dans Docker, pourra joindre ce service macOS avec :

```text
http://host.docker.internal:8001/mcp
```

Cette méthode conserve la base PostgreSQL, Redis et les données OpenWebUI de MyIA intactes.

Le dépôt de référence MyIA se trouve dans `_reference-myia/` dans l'environnement de test. Pour partir directement du dépôt officiel :

```bash
git clone https://github.com/EsupPortail/esup-myia-mistral-amue.git
cd esup-myia-mistral-amue
```

Configurer MyIA :

```bash
cp .env.example .env
mkdir -p data/postgres data/redis data/openwebui
$EDITOR .env
```

Renseigner au minimum :

```env
ILAAS_API_KEY=...
LITELLM_MASTER_KEY=sk-local-test
LITELLM_SECRET_KEY=change-me
POSTGRES_PASSWORD=change-me
REDIS_PASSWORD=change-me
WEBUI_SECRET_KEY=change-me
WEBUI_URL=http://localhost:3000
```

Démarrer la stack macOS :

```bash
docker compose -f docker-compose.macos.yml up -d
docker compose ps
open http://localhost:3000
```

Créer le premier compte administrateur OpenWebUI si nécessaire. Une fois le compte créé, désactiver l'inscription publique dans `.env` :

```env
ENABLE_SIGNUP=false
```

## 3. Préparer le prototype LimeSurvey

Dans un autre terminal :

```bash
cd /Users/nicktruch/Code/mcp-agent
rm -rf prototype-limesurvey
unzip mcp-limesurvey-master.zip -d prototype-limesurvey
cd prototype-limesurvey/mcp-limesurvey-master
uv sync --all-extras
```

Lancer d'abord les tests du projet :

```bash
uv run pytest
```

## 4. Configurer LimeSurvey et JWT

```bash
cp .env.example .env
$EDITOR .env
```

Configuration minimale pour un premier test local :

```env
FASTMCP_LOG_LEVEL=DEBUG
MCP_SERVER_PORT=8001

LS_API_URL=https://limesurvey.example.org/index.php/admin/remotecontrol
LS_API_USER=user.ia
LS_API_KEY=votre-cle-api-limesurvey

# Mode JWT partagé pour le développement local
JWT_JWKS_URI=
JWT_ISSUER=
JWT_AUDIENCE=
JWT_ALGORITHM=HS256
JWT_SECRET_KEY=dev-secret-change-me

# Configuration du client de démonstration
CLIENT_JWT_SUB=user.ia
CLIENT_JWT_SECRET_KEY=dev-secret-change-me
CLIENT_JWT_ALGORITHM=HS256
CLIENT_LLM_MODEL=mistral-medium
CLIENT_LLM_BASE_URL=http://127.0.0.1:4000/v1
CLIENT_LLM_API_KEY=sk-local-test
CLIENT_MCP_TOOLSET_URL=http://127.0.0.1:8001/mcp
```

Les valeurs suivantes doivent être cohérentes :

- `CLIENT_JWT_SECRET_KEY` doit être identique à `JWT_SECRET_KEY` ;
- `CLIENT_JWT_SUB` doit correspondre à un utilisateur existant dans LimeSurvey ;
- `CLIENT_LLM_API_KEY` doit correspondre à `LITELLM_MASTER_KEY` ;
- `CLIENT_LLM_BASE_URL` pointe vers LiteLLM démarré sur le port `4000`.

Pour un environnement de production, remplacer le secret partagé par une validation OIDC/CAS via `JWT_JWKS_URI`, `JWT_ISSUER` et `JWT_AUDIENCE`.

## 5. Démarrer le serveur MCP

Depuis le dossier du prototype :

```bash
uv run python -m server.app
```

Le serveur écoute sur `http://127.0.0.1:8001`.

Dans un autre terminal :

```bash
curl http://127.0.0.1:8001/health
```

Résultat attendu :

```text
OK
```

Vérifier également la route racine :

```bash
curl http://127.0.0.1:8001/
```

Résultat attendu :

```text
MCP Server is running. Use the /mcp endpoint for interactions.
```

## 6. Tester le serveur MCP

Le serveur expose actuellement :

| Outil | Type | Test initial |
|---|---|---|
| `list_my_surveys` | Lecture | Recommandé en premier |
| `get_lss_generator_skill` | Documentation | Sans effet métier |
| `import_my_survey` | Écriture | À tester uniquement dans un environnement de test |

Avec MCP Inspector :

```bash
npx @modelcontextprotocol/inspector
```

Configurer une connexion Streamable HTTP vers :

```text
http://127.0.0.1:8001/mcp
```

Le client doit envoyer :

```text
Authorization: Bearer <JWT>
```

Le client `client.cli` fourni par le prototype génère automatiquement le JWT de développement à partir de `CLIENT_JWT_SUB` et `CLIENT_JWT_SECRET_KEY`.

## 6 bis. Déclarer le prototype dans LiteLLM existant

Pour tester le routage avec l'instance MyIA déjà déployée :

1. ouvrir l'administration LiteLLM sur `http://localhost:4000` ;
2. ouvrir la section **MCP Servers** ;
3. ajouter un serveur Streamable HTTP ;
4. utiliser l'URL `http://host.docker.internal:8001/mcp` ;
5. configurer l'en-tête `Authorization: Bearer <JWT>` ;
6. vérifier que les outils `list_my_surveys` et `get_lss_generator_skill` sont découverts.

Le JWT de développement doit avoir un claim `sub` correspondant à l'utilisateur LimeSurvey. Pour un test depuis le client fourni, les variables `CLIENT_LLM_BASE_URL` et `CLIENT_LLM_API_KEY` doivent pointer vers l'instance LiteLLM de MyIA :

```env
CLIENT_LLM_MODEL=mistral-medium
CLIENT_LLM_BASE_URL=http://127.0.0.1:4000/v1
CLIENT_LLM_API_KEY=<valeur de LITELLM_MASTER_KEY dans /Users/nicktruch/Code/myia/.env>
```

Ne pas copier la valeur réelle de `LITELLM_MASTER_KEY` dans ce fichier, dans Git ou dans une conversation.

## 7. Tester avec l'agent Mistral

Depuis le dossier du prototype :

```bash
uv run --extra test python -m client.cli
```

Le client utilise le chemin suivant :

```text
client pydantic-ai
    -> serveur MCP LimeSurvey
    -> LimeSurvey Remote Control API
```

Il utilise LiteLLM et Mistral ESR comme modèle compatible OpenAI lorsque `CLIENT_LLM_BASE_URL` pointe vers `http://127.0.0.1:4000/v1`.

Attention : le client de démonstration exécute une demande de création/import de sondage avant de lister les sondages. Utiliser un compte et une instance de test. Ne pas l'exécuter contre une instance de production sans modifier le scénario.

## 8. Scénario recommandé

Commencer par une lecture :

```text
Liste mes sondages LimeSurvey.
```

Puis tester la génération documentaire :

```text
Donne-moi les règles nécessaires pour générer un fichier LSS LimeSurvey.
```

Tester l'écriture seulement ensuite :

```text
Génère un sondage avec une question simple.
Présente-moi le résumé et attends ma confirmation avant l'import.
```

Après l'import, vérifier dans LimeSurvey :

- le sondage a été créé ;
- le propriétaire est le bon utilisateur ;
- les questions sont correctes ;
- le lien du sondage fonctionne ;
- aucune donnée inattendue n'a été importée.

## 9. Test temporaire via LiteLLM

Sur macOS, un conteneur Docker peut joindre un serveur lancé sur l'hôte via :

```text
http://host.docker.internal:8001/mcp
```

Dans l'administration LiteLLM :

1. ouvrir la section MCP Servers ;
2. ajouter un serveur Streamable HTTP ;
3. saisir `http://host.docker.internal:8001/mcp` ;
4. configurer l'en-tête JWT ;
5. vérifier la découverte des outils.

Si LiteLLM est déjà déployé dans `/Users/nicktruch/Code/myia`, cette déclaration suffit pour le test ; il n'est pas nécessaire de modifier `config/litellm_config.yaml` ni de redémarrer PostgreSQL, Redis ou OpenWebUI.

Cette étape valide le routage LiteLLM. Elle ne constitue pas encore l'intégration complète dans OpenWebUI : le bridge `esup-mcp-agent` décrit dans le document d'architecture reste à développer pour gérer proprement la boucle agentique, les confirmations et les permissions par utilisateur.

## 10. Critères de réussite

Le prototype est validé lorsque :

- MyIA démarre avec Mistral ESR ;
- le serveur MCP répond à `/health` ;
- l'authentification JWT fonctionne ;
- `list_my_surveys` retourne uniquement les sondages autorisés ;
- `get_lss_generator_skill` retourne la documentation LSS ;
- l'import est exécuté uniquement après confirmation ;
- les clés API ne figurent pas dans les logs ;
- les appels sont identifiables par utilisateur et par outil ;
- aucun secret n'est committé.

## Dépannage rapide

Afficher les journaux MyIA :

```bash
docker compose logs -f litellm
docker compose logs -f openwebui
```

Afficher les journaux MCP :

```bash
# terminal dans lequel le serveur MCP est lancé
```

Erreurs fréquentes :

| Symptôme | Vérification |
|---|---|
| `401 Unauthorized` | Vérifier les deux secrets JWT et le claim `sub` |
| Utilisateur LimeSurvey introuvable | Vérifier que `CLIENT_JWT_SUB` correspond au compte LimeSurvey |
| Erreur Mistral | Vérifier `ILAAS_API_KEY`, le modèle et `LITELLM_MASTER_KEY` |
| Connexion MCP impossible depuis Docker | Utiliser `host.docker.internal` sur macOS |
| Outil absent | Vérifier l'endpoint `/mcp`, le transport Streamable HTTP et les logs FastMCP |