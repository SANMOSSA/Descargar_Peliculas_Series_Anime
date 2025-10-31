import os
import platform
import requests
from urllib.parse import urlparse
from animeflv import AnimeFLV
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re

class GestorDescargas:
    def __init__(self):
        sistema = platform.system()
        if sistema == "Windows":
            self.ruta_base = "M:/codigo_propio/descargar_peliculas_series/peliculas_test"
        else:
            self.ruta_base = os.path.abspath("Multimedia")

    @staticmethod
    def obter_video_cargado(url: str) -> str | None:
        try:
            respuesta = requests.get(url, timeout=10)
            if respuesta.status_code not in (200, 301, 302):
                return None
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url)
                page.wait_for_selector("video")
                src = page.get_attribute("video", "src")
                browser.close()
                return src
        except PlaywrightTimeoutError:
            return None
        except Exception as e:
            print("Error:", e)
            return None

    def obtener_extension_real(self, url):
        parsed = urlparse(url)
        ext = os.path.splitext(parsed.path)[1].lower()
        if ext:
            return ext
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

    def obtener_nombre_anime_desde_url(self, url):
        respuesta = requests.get(url)
        if respuesta.status_code not in (200, 301, 302):
            print(f"Error al acceder a la URL del anime. Código de estado: {respuesta.status_code} error: {respuesta.text}")
            return None
        with AnimeFLV() as aflv:
            id_anime = url.split("/")[-1]
            i = 10
            while i > 0:
                try:
                    anime = aflv.get_anime_info(id_anime)
                    nombre_limpio = re.sub(r'[^a-zA-Z0-9 ]', '', anime.title)
                    return nombre_limpio
                except Exception as e:
                    print("Error:", e)
                    i -= 1
            print("No se pudo obtener la información del anime después de varios intentos.")
        return None
    
    def descargar_anime_con_progreso(self, url, nombre_anime):
        id_anime = url.split("/")[-1]
        ruta_categoria = os.path.join(self.ruta_base, "Animes", nombre_anime, "Season 01")
        os.makedirs(ruta_categoria, exist_ok=True)
        episodios_descargados = {}
        episodios_fallidos = {}
        servidores_alternos = {}
        with AnimeFLV() as aflv:
            while True:
                try:
                    anime = aflv.get_anime_info(id_anime)
                    break
                except Exception as e:
                    pass
            total_eps = len(anime.episodes)
            eps_procesados = 0
            anime.episodes.reverse()
            for episodio in anime.episodes:
                if episodio.id > 12:
                    eps_procesados += 1
                    continue
                nombre_episodio = f"{nombre_anime} S01.E{str(episodio.id).zfill(3)}"
                ruta_episodio = os.path.join(ruta_categoria, f"{nombre_episodio}")
                servidores_descarga = aflv.get_links(id_anime, episodio.id)
                descargado = False
                for servidor in servidores_descarga:
                    if servidor.server == "Stape":
                        porcentaje = eps_procesados / total_eps * 100
                        yield porcentaje, "Buscando video ..."
                        video_src = GestorDescargas.obter_video_cargado(servidor.url)
                        if video_src:
                            if video_src.startswith("//"):
                                video_src = "https:" + video_src
                            ext_real = self.obtener_extension_real(video_src)
                            if not ext_real:
                                episodios_fallidos[episodio.id] = "No se pudo determinar la extensión del archivo."
                                continue
                            ruta_final = ruta_episodio + ext_real
                            
                            try:
                                with requests.get(video_src, stream=True) as r:
                                    r.raise_for_status()
                                    total = int(r.headers.get('Content-Length', 0))
                                    if os.path.exists(ruta_final) and os.path.getsize(ruta_final) == total:
                                        eps_procesados += 1
                                        porcentaje = eps_procesados / total_eps * 100
                                        mensaje = f"✅ Episodio {episodio.id} ya descargado ({eps_procesados}/{total_eps})"
                                        descargado = True
                                        yield porcentaje, mensaje
                                        continue
                                    descargado_bytes = 0
                                    with open(ruta_final, 'wb') as f:
                                        for chunk in r.iter_content(chunk_size=1024*1024):
                                            if chunk:
                                                f.write(chunk)
                                                descargado_bytes += len(chunk)
                                                if total:
                                                    porcentaje = (eps_procesados + descargado_bytes / total) / total_eps * 100
                                                    episodio_actual = f"{episodio.id}/{total_eps}"
                                                    megas_descargadas =f"({descargado_bytes / (1024*1024):.2f}/{total / (1024*1024):.2f} MB)"
                                                    mensaje = f"⬇️ Descargando episodio {episodio_actual} {megas_descargadas}"
                                                    yield porcentaje, mensaje
                                episodios_descargados[episodio.id] = ruta_final
                                eps_procesados += 1
                                porcentaje = eps_procesados / total_eps * 100
                                mensaje = f"✅ Episodio {episodio.id} descargado ({eps_procesados}/{total_eps})"
                                yield porcentaje, mensaje
                                descargado = True
                            except requests.RequestException as e:
                                episodios_fallidos[episodio.id] = f"Error al descargar: {str(e)}"
                            break
                    else:
                        if episodio.id not in servidores_alternos:
                            servidores_alternos[episodio.id] = ""
                        servidores_alternos[episodio.id] += f"{servidor.server}: {servidor.url}\n"
                if not descargado:
                    mensaje = f"❌ Episodio {episodio.id} fallido"
                    eps_procesados += 1
                    porcentaje = eps_procesados / total_eps * 100
                    episodios_fallidos[episodio.id] = "No se pudo descargar desde Stape."
                    yield porcentaje, mensaje
            mensaje_final = f"**Descargados:** {eps_procesados-len(episodios_fallidos)} de {total_eps} episodios.\n"
            if episodios_fallidos:
                mensaje_final += f"**Fallidos:** {len(episodios_fallidos)}\n\n"
                mensaje_final += "**Servidores alternos:**\n"
                for ep_id, enlaces in servidores_alternos.items():
                    if ep_id in episodios_fallidos:
                        mensaje_final += f"- Episodio `{ep_id}`:\n"
                        for enlace in enlaces.strip().split('\n'):
                            if enlace:
                                mensaje_final += f"  - {enlace}\n"
            else:
                mensaje_final += "**Todos los episodios descargados correctamente.**"
            yield 100, mensaje_final

    
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
        if os.path.exists(ruta_archivo):
            yield 100
        else:
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