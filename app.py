import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

import streamlit as st
import pandas as pd
import datetime as dt

import drive_io as dio

st.set_page_config(page_title="UDB IA - Procesador", layout="centered")

st.title("UDB IA - Procesador de Documentos")
st.write("Subí un archivo, procesá y descargá el resultado.")

ROOT_ID = st.secrets.get("DRIVE_ROOT_FOLDER_ID")
if not ROOT_ID:
    st.error("Falta configurar DRIVE_ROOT_FOLDER_ID en Secrets.")
    st.stop()

sa_info_raw = st.secrets.get("gcp_service_account")
if not sa_info_raw:
    st.error("Falta configurar gcp_service_account en Secrets.")
    st.stop()

try:
    sa_info = dict(sa_info_raw)
except Exception:
    import json
    sa_info = json.loads(json.dumps(sa_info_raw))

drive = dio.get_drive(sa_info)
input_id = dio.ensure_subfolder(drive, ROOT_ID, "input")
output_id = dio.ensure_subfolder(drive, ROOT_ID, "output")
logs_id = dio.ensure_subfolder(drive, ROOT_ID, "logs")

st.subheader("1) Cargar archivo a Drive (input)")
up = st.file_uploader("Elegí un archivo (CSV, XLSX, PDF, TXT, etc.)", type=None)
if up and st.button("Subir a Drive"):
    file_bytes = up.read()
    dio.upload_bytes(drive, input_id, up.name, file_bytes)
    dio.append_log_csv(drive, logs_id, f"{dt.datetime.now().isoformat()},upload,{up.name},ok,")
    st.success(f"Subido: {up.name}")

st.subheader("Archivos disponibles en input/")
files = dio.list_files(drive, input_id)
if files:
    df = pd.DataFrame([{"name": f["name"], "id": f["id"], "mimeType": f.get("mimeType", "")} for f in files])
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Aún no hay archivos en input/.")

st.subheader("2) Procesar")
choices = [f["name"] for f in files] if files else []
chosen = st.selectbox("Elegí un archivo de input/ para procesar", choices)

if st.button("Procesar"):
    if not chosen:
        st.warning("Elegí un archivo primero.")
    else:
        src = next(f for f in files if f["name"] == chosen)
        out_name = f"PROCESADO_{chosen}"
        text = dio.download_string(drive, src["id"])
        if text is not None:
            new_text = f"Procesado por UDB IA - {dt.datetime.now().isoformat()}\n\n{text}"
            dio.upload_bytes(drive, output_id, out_name, new_text.encode("utf-8"), "text/plain")
        else:
            blob = dio.download_bytes(drive, src["id"])
            dio.upload_bytes(drive, output_id, out_name, blob, src.get("mimeType", "application/octet-stream"))
        dio.append_log_csv(drive, logs_id, f"{dt.datetime.now().isoformat()},process,{chosen},ok,")
        st.success(f"Listo. Generado en output/: {out_name}")

st.subheader("Resultados en output/")
out_files = dio.list_files(drive, output_id)
if out_files:
    df2 = pd.DataFrame([{"name": f["name"], "id": f["id"], "mimeType": f.get("mimeType", "")} for f in out_files])
    st.dataframe(df2, use_container_width=True, hide_index=True)
else:
    st.info("Aún no hay archivos en output/.")

st.caption("© UDB Matemática - UTN-FRGP | App demo.")
