import json
from urllib.parse import urlparse
import gradio as gr
from utils.validators import validar_url
from utils.file_utils import guardar_config
from ui.components import barra_html

def obtener_nombres_animes(lista_animes):
    return [cat["nombre"] for cat in lista_animes]

def agregar_anime(url, lista_animes, gestor, ruta_config):
    existente = next((cat for cat in lista_animes if cat["url"].strip() == url.strip()), None)
    if existente:
        return f"El anime ya existe.", gr.Dropdown(choices=obtener_nombres_animes(lista_animes), value=existente["nombre"])
    
    if not validar_url(url):
        return "URL no válida.", gr.Dropdown(choices=obtener_nombres_animes(lista_animes), value=None)
    
    nombre = gestor.obtener_nombre_anime_desde_url(url)
    if not nombre:
        return "No se pudo obtener el nombre del anime desde la URL.", gr.Dropdown(choices=obtener_nombres_animes(lista_animes), value=None)
    
    existente = next((cat for cat in lista_animes if cat["nombre"].strip() == url.strip()), None)
    if existente:
        return f"El anime ya existe.", gr.Dropdown(choices=obtener_nombres_animes(lista_animes), value=existente["nombre"])

    lista_animes.append({"nombre": nombre, "url": url})
    guardar_config(ruta_config, "lista_animes", lista_animes)
    return f"Anime: '{nombre}' agregado correctamente.", gr.Dropdown(choices=obtener_nombres_animes(lista_animes), value=nombre)

def buscar_episodios(nombre_anime, lista_animes, gestor):
    for cat in lista_animes:
        yield barra_html(0), "Empezando búsqueda..."
        if cat["nombre"] == nombre_anime:
            progreso = gestor.descargar_anime_con_progreso(cat['url'], nombre_anime)
            for porcentaje, mensaje in progreso:
                yield barra_html(porcentaje), mensaje
            break
        else:
            yield barra_html(0), "Categoría no encontrada."
    else:
        yield barra_html(0), "Categoría no encontrada."