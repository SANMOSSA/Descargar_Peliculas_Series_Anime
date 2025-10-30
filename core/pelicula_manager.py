from utils.validators import validar_url, limpiar_nombre_archivo
from ui.components import barra_html

def descargar_pelicula(categoria, link, nombre, gestor, categorias_peliculas):
    if not categoria or categoria not in categorias_peliculas:
        yield barra_html(0), "Categoría no válida."
        return
    if not validar_url(link):
        yield barra_html(0), "Link no válido."
        return
    nombre_sanitizado = limpiar_nombre_archivo(nombre)
    if not nombre_sanitizado:
        yield barra_html(0), "Nombre de archivo no válido."
        return

    for progreso in gestor.descargar_pelicula_con_progreso(categoria, link.strip(), nombre_sanitizado):
        yield barra_html(progreso), f"Descargando... {progreso:.2f}%"

    yield barra_html(100), f"✅ Película descargada en {gestor.ruta_base}/Peliculas/{categoria}/{nombre_sanitizado}"