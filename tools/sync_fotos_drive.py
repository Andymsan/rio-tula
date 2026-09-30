# -*- coding: utf-8 -*-
"""
Descarga fotos nuevas de la carpeta de Google Drive de Ariel y las coloca en
img/fotos/<sección>/ con el nombre que ya usa el sitio.

Convención de nombres en Drive (recorre la carpeta y todas sus subcarpetas,
por ejemplo "6_Ecosistemas" dentro de la carpeta principal):
    <seccion>_<orden>_<pie de foto>.<ext>
    ejemplo: ecosistemas-4_41_ACTUAL - Zona inundable Tres Culturas.jpg
donde <seccion> es el id de una sección de TEXTOS.md (p. ej. "ecosistemas-3").
Se separa solo en los primeros DOS guiones bajos; el resto del nombre
(incluyendo guiones bajos) se usa tal cual como pie de foto.

Requiere una cuenta de servicio de Google con acceso de lectura a la carpeta
(variable de entorno GDRIVE_SA_KEY con el JSON completo de la cuenta de
servicio) y el id de la carpeta (GDRIVE_FOLDER_ID). Se corre normalmente
desde GitHub Actions (.github/workflows/sync-fotos.yml); también se puede
correr a mano:

    set GDRIVE_SA_KEY=... (el JSON de la cuenta de servicio)
    set GDRIVE_FOLDER_ID=1meBL5gB6a3n2BgOZr6xZl221GEdamP3O
    python tools/sync_fotos_drive.py
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS_DIR = os.path.join(ROOT, "img", "fotos")

IMAGENES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def parse_nombre(nombre_drive, mime_type):
    """'ecosistemas-4_41_ACTUAL - Zona inundable.jpg' -> ('ecosistemas-4', '41_ACTUAL - Zona inundable.jpg')

    La extensión se toma del tipo real del archivo (mimeType), no del nombre:
    Drive a veces sube fotos sin que el nombre visible traiga extensión."""
    base, _ = os.path.splitext(nombre_drive)
    partes = base.split("_", 2)
    if len(partes) != 3 or not partes[1].strip():
        return None
    seccion, orden, pie = partes
    return seccion, "%s_%s%s" % (orden, pie, IMAGENES[mime_type])


def main():
    sa_key = os.environ.get("GDRIVE_SA_KEY")
    folder_id = os.environ.get("GDRIVE_FOLDER_ID")
    if not sa_key or not folder_id:
        print("Faltan GDRIVE_SA_KEY o GDRIVE_FOLDER_ID.", file=sys.stderr)
        sys.exit(1)

    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload

    creds = service_account.Credentials.from_service_account_info(
        json.loads(sa_key), scopes=["https://www.googleapis.com/auth/drive.readonly"])
    drive = build("drive", "v3", credentials=creds)

    CARPETA = "application/vnd.google-apps.folder"
    nuevos = []
    ignorados = []
    por_visitar = [folder_id]
    while por_visitar:
        actual = por_visitar.pop(0)
        page_token = None
        while True:
            resp = drive.files().list(
                q="'%s' in parents and trashed = false" % actual,
                fields="nextPageToken, files(id, name, mimeType)",
                pageToken=page_token,
            ).execute()
            for f in resp.get("files", []):
                if f["mimeType"] == CARPETA:
                    por_visitar.append(f["id"])  # subcarpeta (p. ej. "6_Ecosistemas"): también se revisa
                    continue
                if f["mimeType"] not in IMAGENES:
                    continue
                parsed = parse_nombre(f["name"], f["mimeType"])
                if not parsed:
                    ignorados.append(f["name"])
                    continue
                seccion, archivo = parsed
                destino = os.path.join(FOTOS_DIR, seccion, archivo)
                if os.path.exists(destino):
                    continue  # ya la tenemos
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                buf = io.BytesIO()
                downloader = MediaIoBaseDownload(buf, drive.files().get_media(fileId=f["id"]))
                done = False
                while not done:
                    _, done = downloader.next_chunk()
                open(destino, "wb").write(buf.getvalue())
                nuevos.append(os.path.join("img", "fotos", seccion, archivo))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    if ignorados:
        print("Nombres que no siguen la convención <seccion>_<orden>_<pie> (se ignoraron):")
        for n in ignorados:
            print("  -", n)
    if nuevos:
        print("Fotos nuevas:")
        for n in nuevos:
            print("  +", n)
    else:
        print("Sin fotos nuevas.")

    # para que el workflow sepa si debe reconstruir el sitio
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        with open(gh_output, "a", encoding="utf-8") as fh:
            fh.write("nuevas=%s\n" % ("1" if nuevos else "0"))


if __name__ == "__main__":
    main()
