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
import os, re, sys
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOTOS_DIR = os.path.join(ROOT, "img", "fotos")

IMAGENES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
EXTS_CONOCIDAS = (".jpg", ".jpeg", ".png", ".webp")
VIDEOS = {"video/mp4", "video/quicktime", "video/webm", "video/x-matroska", "video/x-m4v"}
EXTS_VIDEO = (".mp4", ".mov", ".m4v", ".webm", ".mkv")
VIDEO_DIR = os.path.join(ROOT, "img", "video")


def nombre_video(nombre_drive):
    """'portada_1_Ribera.mov' -> 'portada_1' (el pie de foto no se usa en los videos)."""
    base = nombre_drive
    if nombre_drive.lower().endswith(EXTS_VIDEO):
        base, _ = os.path.splitext(nombre_drive)
    partes = base.split("_", 2)
    if len(partes) < 2 or not partes[0].strip():
        return None
    orden = partes[1].strip() if partes[1].strip().isdigit() else "50"
    return "%s_%s" % (partes[0].strip(), orden)


def convertir_video(origen, destino_mp4):
    """Convierte a dos MP4 livianos (H.264, sin audio): normal (<=1280 px, 20 s) y para celular (_m: 640 px, 12 s, ~1 MB),
    y guarda un póster JPG. Necesita ffmpeg."""
    import subprocess
    poster = destino_mp4[:-4] + ".jpg"
    movil = destino_mp4[:-4] + "_m.mp4"
    if not os.path.exists(destino_mp4):
        subprocess.run(["ffmpeg", "-y", "-i", origen, "-t", "20", "-an", "-vf", "scale='min(1280,iw)':-2,fps=24",
                        "-c:v", "libx264", "-crf", "29", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", destino_mp4],
                       check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-ss", "1", "-i", destino_mp4, "-frames:v", "1", "-q:v", "4", poster], check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-i", origen, "-t", "12", "-an", "-vf", "scale='min(640,iw)':-2,fps=20",
                    "-c:v", "libx264", "-crf", "32", "-preset", "medium", "-profile:v", "main", "-pix_fmt", "yuv420p", "-movflags", "+faststart", movil],
                   check=True, capture_output=True)


# erratas frecuentes en los nombres de archivo de Drive (se corrigen al traer la foto)
CORRECCIONES = [("Cuautilán", "Cuautitlán"), ("ROsas", "Rosas"), ("deBojay", "de Bojay"), ("manatial", "manantial"),
                ("Febrero", "febrero"), ("10km", "10 km")]


def parse_nombre(nombre_drive, mime_type):
    """'ecosistemas-4_41_ACTUAL - Zona inundable.jpg' -> ('ecosistemas-4', '41_ACTUAL - Zona inundable.jpg')
    El número de orden es opcional: 'promesa-1_Presidenta en la toma de protesta.jpg' también vale.

    La extensión se toma del tipo real del archivo (mimeType), no del nombre:
    Drive a veces sube fotos sin que el nombre visible traiga extensión, y en
    ese caso NO hay que recortar nada (ojo con pies de foto con números
    decimales, como "Más de 1.5 m de azolve": ahí el ".5..." no es una
    extensión, aunque tenga un punto)."""
    base = nombre_drive
    if nombre_drive.lower().endswith(EXTS_CONOCIDAS):
        base, _ = os.path.splitext(nombre_drive)
    partes = base.split("_", 1)
    if len(partes) != 2 or not partes[0].strip() or not partes[1].strip():
        return None
    seccion, resto = partes[0].strip(), partes[1]
    m = re.match(r"^(\d+)_(.+)$", resto)
    orden, pie = (m.group(1), m.group(2)) if m else ("50", resto)  # sin número: se acomoda al final, en orden alfabético
    pie = pie.strip()
    for malo, bueno in CORRECCIONES:
        pie = pie.replace(malo, bueno)
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
                if f["mimeType"] in VIDEOS or f["name"].lower().endswith(EXTS_VIDEO):
                    nv = nombre_video(f["name"])
                    if not nv:
                        ignorados.append(f["name"]); continue
                    destino_v = os.path.join(VIDEO_DIR, nv + ".mp4")
                    if os.path.exists(destino_v) and os.path.exists(destino_v[:-4] + "_m.mp4"):
                        continue
                    os.makedirs(VIDEO_DIR, exist_ok=True)
                    tmp = os.path.join(VIDEO_DIR, "_descarga.tmp")
                    with open(tmp, "wb") as fh:
                        dl = MediaIoBaseDownload(fh, drive.files().get_media(fileId=f["id"]), chunksize=20 * 1024 * 1024)
                        listo = False
                        while not listo:
                            _, listo = dl.next_chunk()
                    try:
                        convertir_video(tmp, destino_v)
                        nuevos.append(os.path.join("img", "video", nv + ".mp4"))
                    except Exception as e:
                        print("  (no se pudo convertir el video %s: %s)" % (f["name"], e))
                    finally:
                        if os.path.exists(tmp):
                            os.remove(tmp)
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
                try:
                    from optimizar_fotos import optimizar
                    optimizar(destino)
                except Exception as e:
                    print("  (no se pudo optimizar %s: %s)" % (archivo, e))
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
