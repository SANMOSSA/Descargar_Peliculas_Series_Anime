import gradio as gr
from functools import partial
from core.anime_manager import obtener_nombres_animes, buscar_episodios, agregar_anime,obtener_datos_anime

def crear_tab_animes(lista_animes, gestor, ruta_config):
    def actualizar_drop():
        return gr.Dropdown(
            label="Selecciona un anime",
            choices=obtener_nombres_animes(ruta_config),
            interactive=True
        )
    with gr.Tab("Buscar episodios nuevos"):
        with gr.Row(equal_height=True):
            actualizar = gr.Button("🔃", size="sm", scale=1)
            dropdown_cat = gr.Dropdown(
            label="Selecciona un anime",
            choices=obtener_nombres_animes(ruta_config),
            value=obtener_nombres_animes(ruta_config)[0] if obtener_nombres_animes(ruta_config) else None,
            interactive=True,
            scale=4
            )
        btn_ejecutar = gr.Button("Buscar nuevos episodios")

        barra_progreso_anime = gr.HTML()
        salida_proceso = gr.Markdown("Proceso...")
        datos_anime = gr.HTML("Aqui va el poster")
        actualizar.click(fn=actualizar_drop, outputs=dropdown_cat)
        buscar_fn = partial(
            buscar_episodios, lista_animes=lista_animes, gestor=gestor)
        btn_ejecutar.click(
            buscar_fn,
            inputs=dropdown_cat,
            outputs=[barra_progreso_anime, salida_proceso]
        )
        datos_fn = partial(
            obtener_datos_anime,lista_animes=lista_animes, gestor=gestor)
        dropdown_cat.change(datos_fn, inputs=dropdown_cat, outputs=datos_anime)

    with gr.Tab("Agregar nuevo anime"):
        url_input = gr.Textbox(
            label="URL del anime en AnimeFLV (LAS PELICUALAS NO SE DESCARGAN AQUÍ)")
        btn_guardar = gr.Button("Guardar anime (NO DESCARGA)")
        salida_guardar = gr.Textbox(label="Estado")
        agregar_fn = partial(agregar_anime, lista_animes=lista_animes,
                             gestor=gestor, ruta_config=ruta_config)
        btn_guardar.click(
            agregar_fn,
            inputs=[url_input],
            outputs=[salida_guardar, dropdown_cat]
        )
