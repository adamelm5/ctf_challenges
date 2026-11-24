# Architecture du laboratoire

## Services

| Service | Rôle | Accès joueur |
|---|---|---|
| `portal` | Interface web, proxy API, création d'un cookie de session signé | Seul service publié, sur loopback hôte |
| `ctf-controller` | Progression par session, validation des réponses, score, verrou du flag | Non publié; API accessible via le portail |
| `dns-client` | Génère le rapport d'audit simulé à partir de l'autorité de scénario | Réseau interne seulement |
| `dns-authoritative` | Fournit un enregistrement de démonstration par HTTP | Réseau interne seulement; ce n'est pas un serveur DNS |
| `archive` | Exécute comme utilisateur non privilégié `archive`, expose des diagnostics inertes et l'accès contrôlé au flag | Réseau interne seulement |
| `archive-data` | Initialise le volume de données à partir du secret local | Sans réseau; exécution ponctuelle |

## Segmentation

- `player_net` ne contient que le portail.
- `control_net` relie le portail au contrôleur.
- `dns_net` relie le contrôleur, le client DNS et l'autorité simulée.
- `archive_net` relie le contrôleur à l'archive.
- `archive-data` utilise `network_mode: none`.

Le contrôleur est multi-hébergé pour joindre les deux services de preuve. Le
portail n'est pas membre des réseaux DNS ou archive et ne peut pas accéder
directement à leurs endpoints. Les services internes ne publient aucun port.

## Progression et secrets

Le portail crée un identifiant aléatoire, signé avec le jeton interne, et le
place dans un cookie `HttpOnly` / `SameSite=Strict`. Le contrôleur maintient
une progression isolée par identifiant de session. Le cookie n'est pas un
mécanisme d'authentification destiné à un déploiement public.

Le secret n'est monté que dans `archive-data`, qui le copie dans un volume
Docker. Ce volume est ensuite monté en lecture seule sous l'utilisateur
`archive`. Ni le portail ni le contrôleur ne montent le secret ou le volume.
Après validation du parcours, le contrôleur demande le flag à l'endpoint
interne de l'archive avec un jeton de service.

La progression et le score sont en mémoire et repartent à zéro au
redémarrage du contrôleur. Le volume du flag est conservé par défaut.

## Limite de simulation

Les services ne contiennent aucune bibliothèque vulnérable correspondant aux
CVE annoncées. Le « DNS » de ce dépôt est une API HTTP de scénario; TLS et
Log4j/JNDI sont des constats statiques de simulation. Le parcours évalue des
conclusions, pas l'exploitation des vulnérabilités.
