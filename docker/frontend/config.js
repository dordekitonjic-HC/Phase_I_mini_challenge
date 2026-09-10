/* Lege diese Datei per Ansible-Template an (Stichwort: Templating).
 * Standard: gleiche Herkunft (Frontend-Nginx proxyt /api/* auf die api-VM),
 * daher API_BASE_URL leer lassen. Nur für lokale Entwicklung ohne
 * Reverse Proxy hier die API-Adresse eintragen, z. B. "http://127.0.0.1:5000".
 */
window.APP_CONFIG = {
  API_BASE_URL: "http://192.168.56.13:5000",
  APP_NAME: "phase1-mini-app"
};
