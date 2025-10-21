import os
import platform
import requests
from urllib.parse import urlparse

class GestorDescargas:
    def __init__(self):
        sistema = platform.system()
        if sistema == "Windows":
            # Ruta base para Windows si montas volumen ahí
            self.ruta_base = "M:/codigo_propio/descargar_peliculas_series/peliculas_test"
        else:
            # Ruta base estándar para Linux/Docker
            self.ruta_base = "/mnt/Multimedia"

    def obtener_extension_real(self, url):
        """
        Intenta deducir la extensión del archivo desde la URL o el Content-Type HTTP.
        Devuelve la extensión con punto (ej: '.mp4') o cadena vacía si no puede determinarla.
        """
        # 1. Intentar desde la URL misma
        parsed = urlparse(url)
        ext = os.path.splitext(parsed.path)[1].lower()
        if ext:
            return ext

        # 2. Intentar desde Content-Type con una solicitud HEAD
        try:
            head = requests.head(url, allow_redirects=True, timeout=10)
            mime = head.headers.get("Content-Type", "").lower()
            mime_map = {
                "video/mp4": ".mp4",
                "video/x-matroska": ".mkv",
                "video/x-msvideo": ".avi",
                "video/quicktime": ".mov",
                "video/x-flv": ".flv",
                "video/webm": ".webm"
            }
            return mime_map.get(mime, "")
        except Exception:
            return ""

    def descargar_pelicula_con_progreso(self, categoria, url, nombre_base):
        """
        Descarga un archivo de vídeo con progreso.
        Detecta automáticamente su extensión y la añade al nombre_base.
        """
        # Detectar extensión real
        ext_real = self.obtener_extension_real(url)
        if not ext_real:
            yield 0
            yield f"No se pudo determinar la extensión del archivo desde la URL o Content-Type."
            return

        # Crear carpeta de categoría
        ruta_categoria = os.path.join(self.ruta_base, "Peliculas", categoria)
        os.makedirs(ruta_categoria, exist_ok=True)

        # Nombre final con extensión real
        nombre_final = os.path.basename(nombre_base.strip()) + ext_real
        ruta_archivo = os.path.join(ruta_categoria, nombre_final)

        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get('Content-Length', 0))
                descargado = 0

                with open(ruta_archivo, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):  # 1 MB
                        if chunk:
                            f.write(chunk)
                            descargado += len(chunk)
                            if total:
                                porcentaje = descargado / total * 100
                                yield porcentaje
                            else:
                                yield 0

            yield 100
        except requests.RequestException as e:
            yield 0