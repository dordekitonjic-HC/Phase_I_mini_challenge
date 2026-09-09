# phase1-mini-app

Kleine Fullstack-Demo für die Phase-I-Beispielaufgabe (Multi-Server, barebone).
Dient als Deploy-Ziel für Vagrant + Ansible + Docker + PostgreSQL.
Die Infrastrukturaufgabe steht in [`CHALLENGE.md`](CHALLENGE.md).

Zielbild (drei Server):

```text
Client → frontend-VM (Nginx: statische Seite + /api/*-Proxy)
       → api-VM (API im Container) → db-VM (PostgreSQL)
```

## Überblick

- Minimaler Web-Service mit getrenntem Frontend und Backend
- Frontend (`frontend/`, statisch, kein Build-Schritt) mit Status-Dashboard und Notizen
- Backend-API (`backend/`, Flask): Gesundheits-, Info- und DB-Connectivity-Checks plus Notiz-API mit DB-Persistenz (Nachweis für neustartfeste Daten)
- Stateless API (`/health` ohne DB-Abhängigkeit), Stateful Backend (PostgreSQL)
- Konfiguration ausschließlich über Umgebungsvariablen (Backend) bzw. `frontend/config.js` (Frontend)

## Voraussetzungen

- Python 3.12+
- `pip`
- Optional für den DB-Check: erreichbare PostgreSQL-Instanz
- Optional für das Frontend lokal: ein statischer Webserver (z. B. `python -m http.server`)

## Schnellstart

Installiere die Abhängigkeiten und starte die API:

```bash
pip install -r backend/requirements.txt
python backend/app.py
```

Starte das Frontend in einem zweiten Terminal (API-Basis per `frontend/config.js` auf die lokale API zeigen lassen, z. B. `API_BASE_URL: "http://127.0.0.1:5000"`):

```bash
python -m http.server 8080 --directory frontend
```

Öffne danach im Browser `http://127.0.0.1:8080/` oder prüfe die API direkt:

```bash
curl -s http://127.0.0.1:5000/health
curl -s http://127.0.0.1:5000/api/info
```

## Verwendung

Das Frontend spricht die API grundsätzlich über gleiche Herkunft an
(der Frontend-Nginx proxyt `/api/*` auf die api-VM). Nur für lokale
Entwicklung ohne Proxy greift `API_BASE_URL` aus `frontend/config.js`.

| Endpunkt       | Beschreibung                                    | Erfolg        |
|------------------|-------------------------------------------------|---------------|
| `GET /` (Frontend) | Status-Dashboard mit Notizen (HTML)           | `200`         |
| `GET /` (API)    | API-Info, Hostname und Endpunktliste (JSON)     | `200`         |
| `GET /health`    | Liveness-Probe ohne DB-Abhängigkeit             | `200`         |
| `GET /api/hello` | Beispiel-Endpunkt                               | `200`         |
| `GET /api/info`  | Service-Info, Hostname, Uptime, Endpunktliste   | `200`         |
| `GET /api/db`    | DB-Connectivity-Check (`SELECT version()`)      | `200` / `503` |
| `GET /api/notes` | Neueste Notizen (max. 50)                       | `200` / `503` |
| `POST /api/notes`| Notiz anlegen (`{"text": "..."}`)               | `201`/`400`/`503` |

Beispiele:

```bash
curl -s http://127.0.0.1:5000/api/hello
curl -s http://127.0.0.1:5000/api/db
curl -s http://127.0.0.1:5000/api/notes
curl -s -X POST http://127.0.0.1:5000/api/notes \
  -H 'Content-Type: application/json' -d '{"text":"Erste Notiz"}'
```

Bei erreichbarer Datenbank liefert `/api/db` HTTP 200 mit der
PostgreSQL-Version, sonst HTTP 503 mit einer gekürzten Fehlermeldung.

## Konfiguration

| Variable      | Default            | Beschreibung              |
|---------------|--------------------|---------------------------|
| `APP_NAME`    | `phase1-mini-app`  | Service-Name in Antworten |
| `DB_HOST`     | `192.168.56.11`    | Host der PostgreSQL-Instanz |
| `DB_NAME`     | `appdb`            | Datenbankname             |
| `DB_USER`     | `app`              | DB-Benutzer               |
| `DB_PASSWORD` | `changeme`         | DB-Passwort (nur für lokal, sonst per Secret-Management setzen) |

Beispiel:

```bash
APP_NAME=phase1-mini-app DB_HOST=192.168.56.11 python backend/app.py
```

## Projektstruktur

```text
.
├── CHALLENGE.md
├── README.md
├── backend/
│   ├── app.py
│   └── requirements.txt
└── frontend/
    ├── index.html
    └── config.js
```

## Infrastruktur-Übung

Folge [`CHALLENGE.md`](CHALLENGE.md): Richte drei VMs ein (Frontend, API, DB),
provisioniere sie per Ansible, containerisiere Frontend und API mit Docker
und verbinde die API mit PostgreSQL. Lege Vagrantfile, Playbooks,
Dockerfile(s) und Compose-Dateien selbst an.

## Fehlerbehebung

- `GET /api/db → 503`, `GET /api/notes → 503`: Prüfe Erreichbarkeit (`DB_HOST`), Benutzer,
  Passwort und Freigaben der Datenbank. Lege bei Bedarf die Tabelle an
  (`notes` wird beim ersten Zugriff automatisch erzeugt).
- `ModuleNotFoundError: flask`: Führe `pip install -r backend/requirements.txt` aus.
- `Address already in use`: Beende den anderen Prozess auf Port 5000
  oder setze einen freien Port.
