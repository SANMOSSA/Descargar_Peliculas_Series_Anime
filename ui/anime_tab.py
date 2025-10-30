import gradio as gr
from functools import partial
from core.anime_manager import obtener_nombres_animes, buscar_episodios, agregar_anime

def crear_tab_animes(lista_animes, gestor, ruta_config):
    with gr.Tab("Buscar episodios nuevos"):
        dropdown_cat = gr.Dropdown(
            label="Selecciona un anime",
            choices=obtener_nombres_animes(lista_animes),
            value=obtener_nombres_animes(lista_animes)[0] if obtener_nombres_animes(lista_animes) else None,
            interactive=True
        )
        btn_ejecutar = gr.Button("Buscar nuevos episodios")
        barra_progreso_anime = gr.HTML()
        salida_proceso = gr.Markdown("Proceso...")
        buscar_fn = partial(buscar_episodios, lista_animes=lista_animes, gestor=gestor)
        btn_ejecutar.click(
            buscar_fn,
            inputs=dropdown_cat,
            outputs=[barra_progreso_anime, salida_proceso]
        )
        
    with gr.Tab("Agregar nuevo anime"):
        url_input = gr.Textbox(label="URL del anime en AnimeFLV (LAS PELICUALAS NO SE DESCARGAN AQUÍ)")
        btn_guardar = gr.Button("Guardar anime (NO DESCARGA)")
        salida_guardar = gr.Textbox(label="Estado")
        agregar_fn = partial(agregar_anime, lista_animes=lista_animes, gestor=gestor, ruta_config=ruta_config)
        btn_guardar.click(
            agregar_fn,
            inputs=[url_input],
            outputs=[salida_guardar, dropdown_cat]
        )