# Validation et remise à zéro

## Tests

Depuis `scenario-3cve` :

```powershell
python -m unittest discover -s tests -v
docker compose --env-file .env.example config --quiet
```

Les tests couvrent l'authentification entre portail et contrôleur, les étapes
dans l'ordre, les mauvaises réponses, l'accès refusé au flag avant la fin et
l'accès final au flag au principal `archive`. Ils vérifient également que les
sessions n'échangent pas leur progression. Le test HTTP utilise un service DNS
et une archive simulés.

Pour vérifier l'intégration Docker, suivre `installation.md`, puis vérifier
`docker compose ps` et naviguer sur l'URL locale. Les services internes ne
publient pas de port sur l'hôte.

## API locale

L'interface web parle au portail, qui relaie les routes suivantes au contrôleur
avec un jeton de service privé :

- `GET /api/status` — progression et score.
- `GET /api/stages/1`, `/api/stages/2`, `/api/stages/3` — éléments d'une étape
  (les suivantes restent verrouillées jusqu'à la validation précédente).
- `POST /api/stages/{id}/submit` — JSON `{"answer":"..."}`.
- `GET /api/flag` — `403` tant que les trois étapes ne sont pas validées; lecture
  du flag par le service d'archive ensuite.

Le contrôleur n'est pas publié. Le flag se trouve dans un volume séparé, monté
en lecture seule dans `archive`; le contrôleur ne monte pas ce volume. La
progression est en mémoire, et redémarrer `ctf-controller` la réinitialise.
`docker compose down` conserve le volume; `docker compose down -v` le supprime.

## Limites

Ces tests valident le simulateur et le parcours de flag, pas l'exploitation
réelle des trois CVE. Les rapports du DNS et de Log4j sont des données de
scénario; aucune requête DNS wire-format spéciale, aucun crash, aucune
résolution JNDI et aucune charge utile ne sont fournis.
