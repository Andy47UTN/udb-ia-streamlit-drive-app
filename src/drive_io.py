# src/drive_io.py — Google Drive API v3
import io
from typing import Optional, List, Dict
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

_SCOPES = ["https://www.googleapis.com/auth/drive"]

def get_drive(sa_info: dict):
    creds = Credentials.from_service_account_info(sa_info, scopes=_SCOPES)
    return build("drive", "v3", credentials=creds)

def _find_folder(drive, name: str, parent_id: Optional[str]) -> Optional[str]:
    q = ["mimeType='application/vnd.google-apps.folder'", "trashed=false", f"name='{name}'"]
    if parent_id:
        q.append(f"'{parent_id}' in parents")
    res = drive.files().list(q=" and ".join(q), fields="files(id,name)").execute()
    files = res.get("files", [])
    return files[0]["id"] if files else None

def ensure_subfolder(drive, parent_id: str, name: str) -> str:
    found = _find_folder(drive, name, parent_id)
    if found:
        return found
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
    folder = drive.files().create(body=meta, fields="id").execute()
    return folder["id"]

def list_files(drive, folder_id: str) -> List[Dict]:
    q = f"'{folder_id}' in parents and trashed=false"
    res = drive.files().list(q=q, fields="files(id,name,mimeType)").execute()
    return res.get("files", [])

def upload_bytes(drive, folder_id: str, filename: str, data: bytes, mime_type: str = "application/octet-stream") -> str:
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime_type, resumable=False)
    meta = {"name": filename, "parents": [folder_id]}
    f = drive.files().create(body=meta, media_body=media, fields="id").execute()
    return f["id"]

def download_string(drive, file_id: str) -> Optional[str]:
    try:
        buf = io.BytesIO()
        req = drive.files().get_media(fileId=file_id)
        downloader = MediaIoBaseDownload(fd=buf, request=req)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        return buf.getvalue().decode("utf-8")
    except Exception:
        return None

def download_bytes(drive, file_id: str) -> bytes:
    buf = io.BytesIO()
    req = drive.files().get_media(fileId=file_id)
    downloader = MediaIoBaseDownload(fd=buf, request=req)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buf.getvalue()

def append_log_csv(drive, logs_folder_id: str, line: str, log_name: str = "usage.csv"):
    res = drive.files().list(
        q=f"'{logs_folder_id}' in parents and trashed=false and name='{log_name}'",
        fields="files(id,name)"
    ).execute()
    files = res.get("files", [])
    if files:
        fid = files[0]["id"]
        current = download_string(drive, fid) or ""
        if not current.endswith("\n"):
            current += "\n"
        current += line
        media = MediaIoBaseUpload(io.BytesIO(current.encode("utf-8")), mimetype="text/csv", resumable=False)
        drive.files().update(fileId=fid, media_body=media).execute()
    else:
        data = "timestamp,action,filename,status,notes\n" + line
        upload_bytes(drive, logs_folder_id, log_name, data.encode("utf-8"), "text/csv")
