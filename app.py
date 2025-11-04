import json
import gradio as gr
import os
from core.gestor_descargas import GestorDescargas
from ui.pelicula_tab import crear_tab_peliculas
from ui.anime_tab import crear_tab_animes
from ui.series_tab import crear_tab_series
from utils.file_utils import crear_config_inicial

RUTA_CONFIG = os.path.abspath("config.json")
print(f"Ruta de configuración: {RUTA_CONFIG}")
if not os.path.exists(RUTA_CONFIG):
    crear_config_inicial(RUTA_CONFIG)

# Cargar configuración inicial

gestor = GestorDescargas()
config = json.load(open(RUTA_CONFIG, "r", encoding="utf-8"))

# Interfaz principal
with gr.Blocks() as demo:
    with gr.Tab("🎬 Película"):
        crear_tab_peliculas(config["categorias_peliculas"], gestor)

    with gr.Tab("🗾 Animes"):
        crear_tab_animes(config["lista_animes"], gestor, RUTA_CONFIG)

    with gr.Tab("📺 Series"):
        crear_tab_series(gestor)

demo.queue()
demo.launch(server_name="0.0.0.0", server_port=8002)
