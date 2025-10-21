import re
import os
from urllib.parse import urlparse
import gradio as gr
from descargar import GestorDescargas

categorias_opciones = ["Accion", "Animacion", "Comedia", "Historia", "Romance", "Terror"]

gestor = GestorDescargas()

def descargar(categoria, link, nombre):
    def _clean_name(name):
        if not isinstance(name, str):
            return None
        name = name.strip()
        if "." in name:
            name = name.rsplit(".", 1)[0] 
        pattern = re.compile(r'^[\w\-\s\(\)]+([A-Za-z0-9]{1,10})$')
        if not pattern.match(name):
            return None
        return name

    # Validaciones
    if not categoria or categoria not in categorias_opciones:
        yield barra_html(0), "Categoría no válida."
        return
    parsed = urlparse(link.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        yield barra_html(0), "Link no válido."
        return
    nombre_sanitizado = _clean_name(nombre)
    if not nombre_sanitizado:
        yield barra_html(0), "Nombre de archivo no válido."
        return

    # Progreso
    for progreso in gestor.descargar_pelicula_con_progreso(categoria, link.strip(), nombre_sanitizado):
        yield barra_html(progreso), f"Descargando... {progreso:.2f}%"
    yield barra_html(100), f"✅ Película descargada en {gestor.ruta_base}/Peliculas/{categoria}/{nombre_sanitizado}"

def barra_html(porcentaje):
    return f"""
    <div style='width:100%;background-color:#ddd;border-radius:5px'>
        <div style='width:{porcentaje}%;background-color:#4caf50;height:24px;border-radius:5px'></div>
    </div>
    <p style='margin-top:4px'>{porcentaje:.2f}%</p>
    """

with gr.Blocks() as demo:
    gr.Markdown("## 🎬 Descargar película")

    categoria = gr.Dropdown(choices=categorias_opciones, label="Categoría")
    link = gr.Textbox(label="Link de la película")
    nombre = gr.Textbox(label="Nombre del archivo (incluye extensión)")

    barra_progreso = gr.HTML()
    salida = gr.Textbox(label="Estado", interactive=False)

    boton_descargar = gr.Button("Descargar")
    boton_descargar.click(fn=descargar, inputs=[categoria, link, nombre], outputs=[barra_progreso, salida])

demo.launch(server_name="0.0.0.0", server_port=8002)