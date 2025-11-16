import os
import platform
import requests
import yt_dlp
from urllib.parse import urlparse
from animeflv import AnimeFLV
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from concurrent.futures import ThreadPoolExecutor
import threading
import re
import time
import multiprocessing


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
            print( "Error PlaywrightTimeoutError")
            return None
        except Exception as e:
            print("Error:", e)
            return None

    def obtener_datos_anime(self,url:str):
        respuesta = requests.get(url)
        if respuesta.status_code not in (200, 301, 302):
            print(
                f"Error al acceder a la URL del anime. Código de estado: {respuesta.status_code} error: {respuesta.text}")
            return None
        with AnimeFLV() as aflv:
            id_anime = url.split("/")[-1]
            i = 10
            while i > 0:
                try:
                    anime = aflv.get_anime_info(id_anime)
                    datos = {
                        "titulo":anime.title,
                        "poster":anime.poster,
                        "generos": anime.genres,
                        "sinopsis": anime.synopsis,
                        "debut":anime.debut
                    } 
                    return datos
                except Exception as e:
                    print("Error:", e)
                    i -= 1
            print(
                "No se pudo obtener la información del anime después de varios intentos.")
        return None

    def obtener_extension_real(self, url):
        parsed = urlparse(url)
        ext = os.path.splitext(parsed.path)[1].lower()
        if ext:
            return ext
        try:
            head = requests.head(url, allow_redirects=True, timeout=30)
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
        except Exception as e:
            print(e)
            return ""

    def obtener_nombre_anime_desde_url(self, url):
        respuesta = requests.get(url)
        if respuesta.status_code not in (200, 301, 302):
            print(
                f"Error al acceder a la URL del anime. Código de estado: {respuesta.status_code} error: {respuesta.text}")
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
            print(
                "No se pudo obtener la información del anime después de varios intentos.")
        return None


    def descargar_archivo_yt(self, url, ruta_final, index, progress_dict, mensajes, lock, nombre_episodio):
        """
        Descarga un archivo usando yt-dlp con seguimiento de progreso.
        Compatible con el sistema de hilos y barra de progreso original.
        """
        try:
            # Si el archivo ya existe y parece completo, lo omitimos
            if os.path.exists(ruta_final):
                progress_dict[index] = 1.0
                with lock:
                    mensajes[index] = f"✅ {nombre_episodio} ya descargado"
                return

            def progreso(d):
                """
                Callback que actualiza el progreso y mensajes.
                """
                if d['status'] == 'downloading':
                    try:
                        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
                        downloaded_bytes = d.get('downloaded_bytes', 0)
                        progreso_actual = downloaded_bytes / total_bytes if total_bytes else 0
                        progress_dict[index] = progreso_actual
                        mb_actual = downloaded_bytes / (1024 * 1024)
                        mb_total = total_bytes / (1024 * 1024) if total_bytes else 0
                        with lock:
                            mensajes[index] = f"⬇️ {nombre_episodio} ({mb_actual:.2f}/{mb_total:.2f} MB)"
                    except Exception:
                        pass

                elif d['status'] == 'finished':
                    progress_dict[index] = 1.0
                    with lock:
                        mensajes[index] = f"✅ {nombre_episodio} descargado"

            # Configuración de yt-dlp
            ydl_opts = {
                'format': 'best',
                'outtmpl': ruta_final,  # Guardar directamente en ruta_final
                'progress_hooks': [progreso],
                'quiet': True,  # Evita spam en la consola
                'no_warnings': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            # Marcamos como completado con error para no bloquear el flujo
            progress_dict[index] = 1.0
            with lock:
                mensajes[index] = f"❌ Error en {nombre_episodio}: {str(e)}"

    def descargar_archivo(self, url, ruta_final, index, progress_dict, mensajes, lock, nombre_episodio):
        """
        Descarga un archivo con seguimiento de progreso.
        """
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get('Content-Length', 0))
                # Verificar si el archivo ya existe y tiene el tamaño esperado
                if os.path.exists(ruta_final):
                    archivo_peso = os.path.getsize(ruta_final)
                    if total and archivo_peso >= total:
                        progress_dict[index] = 1.0
                        with lock:
                            mensajes[index] = f"✅ {nombre_episodio} ya descargado"
                        return
                downloaded = 0
                with open(ruta_final, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):  # 1MB
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            progress_dict[index] = downloaded / \
                                total if total else 0
                            with lock:
                                mensajes[index] = f"⬇️ {nombre_episodio} ({downloaded/(1024*1024):.2f}/{total/(1024*1024):.2f} MB)"
                progress_dict[index] = 1.0
                with lock:
                    mensajes[index] = f"✅ {nombre_episodio} descargado"
        except Exception as e:
            # marcamos como completado para no bloquear
            progress_dict[index] = 1.0
            with lock:
                mensajes[index] = f"❌ Error en {nombre_episodio}: {str(e)}"

    def descargar_anime_con_progreso(self, url, nombre_anime):
        """
        Descarga todos los episodios en paralelo rindiendo progreso global y mensajes.
        """
        id_anime = url.split("/")[-1]
        ruta_categoria = os.path.join(
            self.ruta_base, "Animes", nombre_anime, "Season 01")
        os.makedirs(ruta_categoria, exist_ok=True)

        episodios_urls = []
        episodios_nombres = []
        episodios_rutas = []
        yield 0, "Obteniendo info"
        with AnimeFLV() as aflv:
            while True:
                try:
                    anime = aflv.get_anime_info(id_anime)
                    break
                except:
                    pass
            anime.episodes.reverse()

            resultados = {}
                        
            numero_eps = len(anime.episodes)
            threads = []
            resultados_lock = threading.Lock()

            def thread_func(episodio, mensaje, resultados):
                res = obtener_link_ep(episodio)
                with resultados_lock:
                    if res[1]:
                        mensaje[res[0]] = f"- ✅ Link {res[0]} obtenido"
                        resultados[res[0]] = res[1:]
                    else:
                        mensaje[episodio.id] = f"- ❌ Link {episodio.id} no obtenido"

            def obtener_link_ep(episodio):
                try:
                    servidores_descarga = aflv.get_links(id_anime, episodio.id)
                    for servidor in servidores_descarga:
                        if servidor.server == "Stape":
                            video_src = GestorDescargas.obter_video_cargado(servidor.url)
                            if video_src:
                                if video_src.startswith("//"):
                                    video_src = "https:" + video_src
                                ext_real = self.obtener_extension_real(video_src)
                                if not ext_real:
                                    print("No hay ext")
                                    return episodio.id, None
                                nombre_episodio = f"{nombre_anime} S01E{str(episodio.id).zfill(3)}"
                                ruta_final = os.path.join(ruta_categoria, nombre_episodio + ext_real)
                                return (episodio.id, video_src, nombre_episodio, ruta_final)
                            else:
                                print("No hay video")
                                return episodio.id, None
                    print("No hay servidor")
                    return episodio.id, None
                except Exception as e:
                    print(e)
                    return episodio.id, None

            # Lanzar los hilos
            episodios = anime.episodes
            # Procesar episodios en lotes de máximo 4 hilos por iteración
            episodios_pendientes = [ep for ep in episodios if ep.id not in resultados]
            mensaje = {}
            while episodios_pendientes:
                threads = []
                lote = episodios_pendientes[:4]
                for episodio in lote:
                    mensaje[episodio.id] = f"- ⏳ Obteniendo link ep {episodio.id}"
                    yield 0, "\n".join(mensaje.values())
                    t = threading.Thread(target=thread_func, args=(episodio, mensaje, resultados))
                    threads.append(t)
                    t.start()
                for t in threads:
                    t.join()
                episodios_pendientes = [ep for ep in episodios if ep.id not in resultados]

            # Ahora sí, los objetos están listos
            resultados = dict(sorted(resultados.items()))
            for resultado in resultados.values():
                if resultado:
                    video_src, nombre_episodio, ruta_final = resultado
                    episodios_urls.append(video_src)
                    episodios_nombres.append(nombre_episodio)
                    episodios_rutas.append(ruta_final)
            yield 0 , "Enlaces obtenidos"


        # Diccionarios para progreso y mensajes
        progress = {i: 0 for i in range(len(episodios_urls))}
        mensajes = {i: f"Ep {i+1} Pendiente" for i in range(len(episodios_urls))}
        lock = threading.Lock()

        # Lanzamos descargas en paralelo usando hilos
        threads = []
        total_eps = len(episodios_urls)
        activos = set()
        i = 0

        while i < total_eps or activos:
            # Lanzar hasta 4 hilos activos
            while len(activos) < 4 and i < total_eps:
                t = threading.Thread(target=self.descargar_archivo, args=(episodios_urls[i], episodios_rutas[i], i, progress, mensajes, lock, episodios_nombres[i]))
                threads.append(t)
                t.start()
                activos.add(t)
                i += 1

            # Esperar a que alguno termine
            for t in list(activos):
                if not t.is_alive():
                    activos.remove(t)

            with lock:
                progreso_global = sum(progress.values()) / total_eps * 100
                mensajes_actuales = list(mensajes.values())
                yield progreso_global, "\n".join([f"- {m}" for m in mensajes_actuales])

            if progreso_global >= 100:
                break
            time.sleep(0.3)
        mensajes_actuales = list(mensajes.values())
        mensajes_actuales.insert(0,"Descarga terminada:")
        yield 100, "\n".join([f"- {m}" for m in mensajes_actuales])

    def descargar_serie_con_progreso(self, json_serie):

        nombre_serie = json_serie["nombre"]
        temporadas = json_serie["temporadas"]

        # Crear carpeta base para la serie
        ruta_serie = os.path.join(self.ruta_base, "Series", nombre_serie)
        os.makedirs(ruta_serie, exist_ok=True)

        episodios_urls = []
        episodios_nombres = []
        episodios_rutas = []

        # Recorrer temporadas y episodios
        for temporada_nombre, episodios_dict in temporadas.items():
            ruta_temporada = os.path.join(ruta_serie, temporada_nombre.capitalize())
            os.makedirs(ruta_temporada, exist_ok=True)

            for numero_ep, url_ep in episodios_dict.items():
                nombre_episodio = f"{nombre_serie} S0{temporada_nombre[-1]}E{str(int(numero_ep)).zfill(3)}"
                ruta_final = os.path.join(ruta_temporada, f"{nombre_episodio}.mp4")  # o la extensión que corresponda

                episodios_urls.append(url_ep)
                episodios_nombres.append(nombre_episodio)
                episodios_rutas.append(ruta_final)

        yield 0, "Enlaces obtenidos"

        # Diccionarios para progreso y mensajes
        progress = {i: 0 for i in range(len(episodios_urls))}
        mensajes = {i: f"Ep {i+1} Pendiente" for i in range(len(episodios_urls))}
        lock = threading.Lock()

        threads = []
        total_eps = len(episodios_urls)
        activos = set()
        i = 0

        # Descarga en paralelo con máximo 4 hilos activos
        while i < total_eps or activos:
            while len(activos) < 4 and i < total_eps:
                t = threading.Thread(
                    target=self.descargar_archivo_yt,
                    args=(episodios_urls[i], episodios_rutas[i], i, progress, mensajes, lock, episodios_nombres[i])
                )
                threads.append(t)
                t.start()
                activos.add(t)
                i += 1

            # Revisar hilos que ya terminaron
            for t in list(activos):
                if not t.is_alive():
                    activos.remove(t)

            # Calcular progreso global
            with lock:
                progreso_global = sum(progress.values()) / total_eps * 100
                mensajes_actuales = list(mensajes.values())
                yield progreso_global, "\n".join([f"- {m}" for m in mensajes_actuales])

            if progreso_global >= 100:
                break

            time.sleep(0.3)

        # Finalización
        mensajes_actuales = list(mensajes.values())
        mensajes_actuales.insert(0, "Descarga terminada:")
        yield 100, "\n".join([f"- {m}" for m in mensajes_actuales])

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