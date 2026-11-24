# Hospital Network — CTF local simulé

Parcours Docker Compose composé du portail, du contrôleur, du client et de
l'autorité DNS simulés, de l'application archive et de son initialiseur de
données. Les trois étapes utilisent des preuves inertes afin d'enseigner
l'analyse et la validation sans reproduire les mécanismes exploitables des
CVE-2016-2107, CVE-2015-7547 ou CVE-2021-44228.

**Ce projet ne constitue pas une reproduction des CVE.** Il n'implémente ni
oracle TLS, ni réponse DNS déclenchant un crash, ni résolution JNDI. Les états
de sécurité affichés sont des données de scénario; ils ne permettent pas de
conclure sur un logiciel réel.

## Démarrage

Depuis `scenario-3cve` dans PowerShell :

```powershell
Copy-Item .env.example .env
New-Item -ItemType Directory -Force secrets
Set-Content -NoNewline secrets\flag 'HOSPITAL{local_test_only}'
docker compose up -d --build
```

Ouvrir <http://127.0.0.1:8080>. Si ce port est occupé, modifier `CTF_PORT` dans
`.env`. Le contrôleur et les services internes n'exposent aucun port sur l'hôte.
Chaque navigateur dispose de sa propre progression.
Le seul secret est monté dans `archive-data`, puis copié dans un volume
accessible en lecture seule par le compte non privilégié `archive`.

Arrêt et remise à zéro de la progression :

```powershell
docker compose down
docker compose up -d
```

La progression est en mémoire et se réinitialise au redémarrage du contrôleur.
Le flag local reste dans `secrets\flag`; il n'est pas supprimé par Compose.
Pour réinitialiser aussi le volume de données, la suppression doit être
explicitement demandée avec `docker compose down -v`.

## Tests

```powershell
python -m unittest discover -s tests -v
docker compose --env-file .env.example config --quiet
```

Le parcours attribue 30/35/25 points aux trois étapes et 10 au flag. Voir
`docs/architecture.md`, `docs/installation.md`, `docs/validation.md` et
`docs/compatibility-matrix.md`.
