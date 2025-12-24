# UDB IA – Procesador de Documentos (Drive)

App Streamlit que sube archivos a una carpeta de Google Drive (input/), los procesa
(de manera simple) y escribe el resultado en output/, además de registrar logs/usage.csv.

## Estructura
- app.py
- requirements.txt
- src/
  - __init__.py
  - drive_io.py

## Secrets en Streamlit Cloud (Settings → Secrets)
```toml
DRIVE_ROOT_FOLDER_ID="TU_FOLDER_ID_DE_DRIVE"

[gcp_service_account]
type = "service_account"
project_id = "…"
private_key_id = "…"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "…"
client_id = "…"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "…"
```
