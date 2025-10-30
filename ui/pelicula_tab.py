import gradio as gr
from functools import partial
from core.pelicula_manager import descargar_pelicula

def crear_tab_peliculas(categorias_peliculas, gestor):
    categoria = gr.Dropdown(choices=categorias_peliculas, label="Categoría")
    link = gr.Textbox(label="Link de la película")
    nombre = gr.Textbox(label="Nombre del archivo (incluye extensión)")
    barra_progreso_peliculas = gr.HTML()
    salida = gr.Textbox(label="Estado", interactive=False)
    boton_descargar = gr.Button("Descargar")

    # Usamos partial para fijar gestor y categorias_peliculas
    descargar_fn = partial(descargar_pelicula, gestor=gestor, categorias_peliculas=categorias_peliculas)

    boton_descargar.click(
        descargar_fn,
        inputs=[categoria, link, nombre],
        outputs=[barra_progreso_peliculas, salida]
    )