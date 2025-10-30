import re
import os
from urllib.parse import urlparse
import gradio as gr
from descargar import GestorDescargas

categorias_opciones = ["Accion", "Animacion", "Comedia", "Historia", "Romance", "Terror"]
categorias_anime = [
    {"nombre": "DanDanDan", "url": "https://www.google.com"},
    {"nombre": "Spyfamily", "url": "https://www.openai.com"},
]

gestor = GestorDescargas()


def obtener_nombres_animes():
    return [cat["nombre"] for cat in categorias_anime]



def buscar_episodios(nombre_anime):
    """Busca la categoría y devuelve la URL para demostrar funcionamiento."""
    for cat in categorias_anime:
        if cat["nombre"] == nombre_anime:
            # Aquí puedes poner el proceso que quieras que se ejecute con la URL
            return f"Ejecutando proceso con URL: {cat['url']}"
    return "Categoría no encontrada."


def agregar_anime(nombre, url):
    """Agrega nueva anime a la lista y devuelve mensaje + lista actualizada."""
    # validar que no exista ya
    if any(cat["nombre"] == nombre for cat in categorias_anime):
        return f"La categoría '{nombre}' ya existe.", gr.Dropdown(choices=obtener_nombres_animes(),value=nombre)
    
    categorias_anime.append({"nombre": nombre, "url": url})
    return f"Categoría '{nombre}' agregada correctamente.", gr.Dropdown(choices=obtener_nombres_animes(),value=nombre)



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
    with gr.Tab("Película"):
        gr.Markdown("## 🎬 Descargar película")

        categoria = gr.Dropdown(choices=categorias_opciones, label="Categoría")
        link = gr.Textbox(label="Link de la película")
        nombre = gr.Textbox(label="Nombre del archivo (incluye extensión)")

        barra_progreso = gr.HTML()
        salida = gr.Textbox(label="Estado", interactive=False)

        boton_descargar = gr.Button("Descargar")
        boton_descargar.click(fn=descargar, inputs=[categoria, link, nombre], outputs=[barra_progreso, salida])
    
    with gr.Tab("Animes"):
        gr.Markdown("## 🎬 Descargar Animes de FLV")
        with gr.Tab("Buscar episodios nuevos"):
            dropdown_cat = gr.Dropdown(
                label="Selecciona un anime",
                choices=obtener_nombres_animes(),
                value=None,
                interactive=True
            )
            btn_ejecutar = gr.Button("Buscar nuevos episodios")
            salida_proceso = gr.Textbox(label="Resultado")
            
            btn_ejecutar.click(
                buscar_episodios,
                inputs=dropdown_cat,
                outputs=salida_proceso
            )
            
        with gr.Tab("Agregar nuevo anime"):
            nombre_input = gr.Textbox(label="Nombre del anime")
            url_input = gr.Textbox(label="URL del anime en AnimeFLV")
            btn_guardar = gr.Button("Guardar anime (NO DESCARGA)")
            salida_guardar = gr.Textbox(label="Estado")
            
            # Al guardar, se actualiza también el dropdown de la otra pestaña
            btn_guardar.click(
                agregar_anime,
                inputs=[nombre_input, url_input],
                outputs=[salida_guardar, dropdown_cat]
        )

demo.launch(server_name="0.0.0.0", server_port=8002)
