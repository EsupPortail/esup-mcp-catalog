# Architecture bridge (archivée)

Ce dossier conserve l'architecture utilisée par le projet avant octobre
2026 : un bridge FastAPI maison qui traduisait les appels MCP en OpenAPI,
pour qu'OpenWebUI (qui ne parlait alors que OpenAPI, pas MCP) puisse
utiliser les serveurs MCP du catalogue.

Depuis, OpenWebUI (≥ v0.6.31) sait se connecter directement à un serveur
MCP en Streamable HTTP (**Panneau d'administration > Réglages >
Intégrations > Serveurs d'outils externes > Type : MCP (Streamable
HTTP)**). Le bridge n'est donc plus nécessaire pour la traduction de
protocole. La doc active est [`../../README.md`](../../README.md) et
[`../../docs/installation.md`](../../docs/installation.md).

## Pourquoi le bridge existait

1. **Traduction de protocole** : OpenWebUI ne consommait que des serveurs
   d'outils OpenAPI, pas MCP. Le bridge exposait chaque outil MCP comme une
   opération OpenAPI (`app.py`, fonction `build_openapi_schema`).
2. **Contournement de sélection par connecteur** : le sélecteur d'outils
   d'OpenWebUI n'active/désactive qu'une connexion entière, pas un outil
   individuel. Le bridge exposait un point d'entrée OpenAPI filtré par
   serveur MCP (`/servers/{name}/openapi.json`) pour que chaque connecteur
   soit sélectionnable séparément — ce qu'OpenWebUI fait nativement
   aujourd'hui, une connexion MCP = un serveur.

Le sous-dossier `docs/` contient une copie figée de `docs/installation.md`
et `docs/cas-usage-datagouv-grist.md` telles qu'elles étaient avant la
simplification, avec le détail des pièges rencontrés à l'époque (en-têtes
CORS, invalidation de session MCP après redémarrage d'un serveur cible,
piège `/openapi.json` doublé dans l'URL, champ "Nom d'utilisateur" trompeur
d'OpenWebUI, nécessité d'un rechargement complet du navigateur après l'ajout
d'une connexion).

## Quand ça pourrait resservir

- Un futur serveur MCP incompatible avec le client MCP natif d'OpenWebUI
  (transport ou mode d'authentification non supporté).
- Une régression du support MCP d'OpenWebUI : sa propre documentation le
  qualifie d'expérimental et en évolution rapide, et indique que
  l'intégration OpenAPI reste la mieux maintenue par son équipe.

Le code (`app.py`) reste fonctionnel tel quel si besoin : il suffit de le
redéployer et de reconnecter OpenWebUI dessus en OpenAPI, comme documenté
dans `README.md` de ce dossier.
