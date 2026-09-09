# DevOps Beispiel-Aufgabe: Multi-Server Infrastruktur (klein)

> Nutze diese Aufgabe zur Vorbereitung auf die Phase-I-Challenge. Arbeite eigenständig: Nur der App-Code ist vorgegeben, erstelle alles andere selbst.

## Toolstack

Verwende: Vagrant, VirtualBox, Linux (Ubuntu Server), Ansible, Docker + Compose, PostgreSQL, Bash, Git

## Aufgabenbeschreibung

Baue eine reproduzierbare Multi-Server-Umgebung für die vorgegebene App aus `backend/` und `frontend/`:

`Client -> frontend-VM (Nginx: statische Seite + /api/*-Proxy) -> api-VM (API im Container) -> db-VM (PostgreSQL)`

Ändere `backend/app.py` sowie `frontend/` nicht inhaltlich (nur `config.js` darf per Templating gerendert werden). Erstelle alles drumherum selbst: VMs, Hardening, Provisionierung, Containerisierung, Vernetzung, Doku. Begründe zentrale Entscheidungen in der Doku.

## Schritte

### 1. Erstelle die Vagrant-Konfiguration

Erstelle ein `Vagrantfile` mit drei Ubuntu-Servern (z. B. `frontend` + `api` + `db`).

Sorge für geeignete Erreichbarkeit: Stelle VM-zu-VM-Kommunikation sicher und mache den Web-Zugriff vom Host aus möglich. Begründe die Netzwerk-Entscheidung (Adressbereich, Weiterleitungen) in der Doku.

Stelle sicher: `vagrant destroy -f && vagrant up` läuft reproduzierbar durch.

### 2. Konfiguriere die VM-Basis

Setze ein geeignetes Benutzer- und Berechtigungskonzept für alle Server um (Stichwort: Least Privilege).

Härte den Fernzugriff gemäß gängiger SSH-Best-Practices. Recherchiere und begründe, welche Auth-Verfahren und Login-Rechte sich für Server eignen.

Weise sicheren Umgang mit System- und Diagnosewerkzeugen nach (Paketverwaltung, Verbindungs-/Routen-/Log-Analyse). Erstelle einen eigenen `healthcheck.sh` mit sauberen Exit-Codes und getrennter Fehlerausgabe.

### 3. Richte Ansible ein

Nutze den Host-Laptop als Control Node.

Bilde das Multi-Server-Setup in Ansible ab und halte die Konfiguration wartbar und wiederverwendbar (Stichworte: Inventory-Struktur mit drei Gruppen, Rollen, Tags). Stelle sicher, dass umgebungsspezifische Konfigurationsdateien dynamisch erzeugbar sind (Stichwort: Templating, z. B. Proxy-Ziele, `config.js`).

Beachte Best Practices zum Secret-Management in Ansible und Git. Stelle sicher, dass ein zweiter Playbook-Lauf keine Änderungen mehr erzeugt (Idempotenz).

### 4. Konfiguriere die Server

Konfiguriere Server `frontend`:

- Deploye die statischen Dateien aus `frontend/` und einen Reverse Proxy. Beachte Best Practices für Pfad-Routing (z. B. `/` vs. `/api/*`) und interne Weiterleitung an die API.
- Stelle sicher, dass Browser ausschließlich mit dem Frontend sprechen (keine direkten API-Aufrufe über VM-Grenzen hinweg nötig).

Konfiguriere Server `api`:

- Installiere die Container-Runtime per Ansible.
- Schreibe ein eigenes `Dockerfile` für `backend/`. Beachte dabei gängige Image-Best-Practices (Build-Effizienz, Versionierung, Dateisystem-Rechte, Zustandsprüfung).
- Deploye die API per Compose. Beachte Best Practices für interne Vernetzung, Persistenz und Neustartverhalten.

Konfiguriere Server `db`:

- Installiere und konfiguriere PostgreSQL per Ansible. Beachte Best Practices für Zugriffskontrolle (wer darf sich woher verbinden).
- Verbinde die API auf `api` mit der DB auf `db`, weise mit `GET /api/db → 200` (aufgerufen über das Frontend) nach.
- Stelle eine regelmäßige, automatisierte Sicherung sicher. Recherchiere geeignete Werkzeuge und Zeitplanung.

Beachte durchgehend IaC-Prinzipien: Vermeide manuelle Klick- und Datei-Deployments, bilde alles als Code ab.

### 5. Dokumentiere

Dokumentiere den Start (`vagrant up` → `ansible-playbook` → Test mit `curl`) und die Architektur (Skizze + 1 Seite: stateless/stateful, L4/L7, Forward/Reverse Proxy, CIDR, SPOF/Backup-Idee). Halte dich kurz. Begründe dort alle Entscheidungen, zu denen oben nur auf Best Practices verwiesen ist.

## Akzeptanzkriterien

Prüfe selbst, erfülle alle Punkte:

- Erstelle alle drei VMs per Vagrant und stelle sicher, dass sie sich gegenseitig erreichen und der Web-Zugriff vom Host über das Frontend funktioniert.
- Weise ein durchdachtes Benutzer-/SSH-Konzept nach (Least Privilege, gängige Hardening-Praktiken, begründet in der Doku).
- Führe die Playbooks idempotent vom Host aus.
- Halte das Repo frei von Klartext-Secrets (begründe die gewählte Secret-Lösung in der Doku).
- Mache das Frontend erreichbar, liefere dort `/` (Dashboard) sowie `/api/*` (`/health`, `/api/hello`, `/api/info`, `/api/notes`) über den Proxy aus.
- Verbinde API mit DB über VM-Grenzen hinweg, liefere `GET /api/db → 200` (über das Frontend aufgerufen).
- Weise persistente Speicherung nach (z. B. per `POST`/`GET /api/notes` über einen Neustart hinweg), erzeuge automatisierte Backups.
- Begründe Image-Aufbau und Compose-Entscheidungen (Build, Rechte, Netz, Persistenz) in der Doku.
- Lege README + Architektur-Doku ab, versioniere den Arbeitsstand nachvollziehbar in Git.

## Hinweise und Best Practices

Beachte und recherchiere selbst:

- Idempotente Ansible-Praktiken (Module vor Shell, Fehlerbehandlung).
- Gängige Dockerfile- und Compose-Praktiken.
- Minimale Angriffsfläche (offene Ports, Firewall, dokumentierter Soll-Zustand).
- Gängige Git-Praktiken (was gehört ins Repo, was nicht, wie Unerwünschtes fernhalten).
- Strukturierte Fehlersuche (schrittweise testen, Logs auswerten).

## Zusatzaufgaben (optional)

- Führe einen Restore-Test des DB-Backups in eine leere DB durch, dokumentiere ihn.
- Richte ein zentrales Logging für alle Server ein.
- Baue ein einfaches Monitoring (z. B. Healthcheck-Cron mit Alert).
- Scanne das Image (z. B. mit Trivy), dokumentiere das Ergebnis.
