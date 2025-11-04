import gradio as gr
from functools import partial
from core.series_manager import descargar_serie


def crear_tab_series(gestor):
    gr.Markdown(
        "# Descargare series Dailymotion\n"
        "Dentro del campo de texto va un JSON que tiene esta estructura:\n"
        "```json\n"
        "{\n"
        "    \"nombre\":\"nombre serie\",\n"
        "    \"temporadas\": {\n"
        "        \"Season 1\": {\n"
        "            \"01\": \"LINK\",\n"
        "            \"02\": \"LINK\",\n"
        "            \"n\": \"LINK\"\n"
        "        },\n"
        "        \"Season 2\": {\n"
        "            \"01\": \"LINK\",\n"
        "            \"02\": \"LINK\",\n"
        "            \"n\": \"LINK\"\n"
        "        },\n"
        "    }\n"
        "}\n"
        "```"
    )
    json_serie = gr.Textbox(label="Json")
    barra_progreso_serie = gr.HTML()
    salida = gr.HTML()
    boton_descargar = gr.Button("Descargar")

    # Usamos partial para fijar gestor y categorias_peliculas
    descargar_fn = partial(descargar_serie, gestor=gestor)

    boton_descargar.click(
        descargar_fn,
        inputs=[json_serie],
        outputs=[barra_progreso_serie, salida]
    )
