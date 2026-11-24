# Matrice de compatibilité

## Services du simulateur livré

| Élément | Valeur |
|---|---|
| Services | `portal`, `ctf-controller`, `dns-client`, `dns-authoritative`, `archive`, `archive-data` |
| Image de base | `python:3.11-slim` |
| Digest | `sha256:673719e071ecf27434fd2635bbd8d00f49f4fdd81f243143438a42ced8bedf60` |
| Système / architecture | image Debian slim; `linux/amd64` observé localement |
| Dépendances | bibliothèque standard Python uniquement |
| Port hôte | TCP 8080 (configurable), publié seulement sur `127.0.0.1` par `portal` |
| Réseaux | `player_net`, `control_net`, `dns_net` et `archive_net`; réseaux internes non publiés |
| Flag | secret local monté dans l'initialiseur; volume lecture seule pour `archive`; absent du contrôleur et du portail |

## Composants CVE

| CVE | État dans ce dépôt |
|---|---|
| CVE-2016-2107 / OpenSSL | Simulation d'analyse seulement; aucun service TLS historique, oracle ou banc d'exploitation |
| CVE-2015-7547 / glibc | Simulation d'audit seulement; aucun paquet DNS spécial, `getaddrinfo()` vulnérable ou crash |
| CVE-2021-44228 / Log4j | Simulation d'analyse seulement; aucune JVM, dépendance Log4j ou requête JNDI |

Les trois étapes ne constituent pas une reproduction fidèle ni un rapport de
validation de ces CVE. Le service `dns-authoritative` est une API HTTP de
scénario, pas un serveur DNS sur le réseau. Les services n'utilisent aucune
dépendance vulnérable. Pour le conteneur DNS existant, le digest de l'image
locale et le patchset complet ne sont pas établis.
