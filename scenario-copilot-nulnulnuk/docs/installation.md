# Installation locale

Prérequis : Docker avec le plugin Compose, et Python 3.11+ pour les tests.

Depuis `scenario-3cve`, dans PowerShell :

```powershell
Copy-Item .env.example .env
New-Item -ItemType Directory -Force secrets
Set-Content -NoNewline secrets\flag 'REMPLACER_PAR_UN_FLAG_LOCAL'
docker compose up -d --build
```

Remplacer la valeur d'exemple par un flag réservé au laboratoire. Le fichier `secrets/flag` et `.env` sont ignorés par Git; ne pas les ajouter au
dépôt. L'initialiseur de données lit le secret et le copie dans un volume; le
service `archive` y accède en lecture seule sous l'UID `10004`.
Le volume conserve son premier flag : pour en définir un autre, exécuter
`docker compose down -v` avant de redémarrer.

Le portail seul est publié sur l'interface locale. Si le port 8080 est déjà
utilisé, ajouter `CTF_PORT=18080` à `.env` puis ouvrir
`http://127.0.0.1:18080`.

Le portail présente les éléments et choix de chaque étape. Le contrôleur refuse
les soumissions hors séquence et n'accorde les 10 derniers points qu'après la
lecture du flag. L'API du contrôleur n'est pas publiée sur l'hôte.

Arrêt :

```powershell
docker compose down
```

Compose ne supprime pas le fichier secret de l'hôte.
