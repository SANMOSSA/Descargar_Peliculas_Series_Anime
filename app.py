import json
import gradio as gr
from core.gestor_descargas import GestorDescargas
from ui.pelicula_tab import crear_tab_peliculas
from ui.anime_tab import crear_tab_animes

RUTA_CONFIG = "Multimedia/config.json"

# Cargar configuración inicial
config = json.load(open(RUTA_CONFIG, "r", encoding="utf-8"))

gestor = GestorDescargas()

# Interfaz principal
with gr.Blocks() as demo:
    with gr.Tab("🎬 Película"):
        crear_tab_peliculas(config["categorias_peliculas"], gestor)

    with gr.Tab("🗾 Animes"):
        crear_tab_animes(config["lista_animes"], gestor, RUTA_CONFIG)

demo.launch(server_name="0.0.0.0", server_port=8002)