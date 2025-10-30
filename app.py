import re
import os
import json
from urllib.parse import urlparse
import gradio as gr
from descargar import GestorDescargas

# categorias_peliculas = ["Accion", "Animacion", "Comedia", "Historia", "Romance", "Terror"]
# lista_animes = [
#     {"nombre": "Lets Play Quest-darake no My Life", "url": "https://www3.animeflv.net/anime/lets-play-questdarake-no-my-life"},
#     {"nombre": "Disney Twisted-Wonderland The Animation Episode of Heartslabyul", "url": "https://www3.animeflv.net/anime/disney-twistedwonderland-the-animation-episode-of-heartslabyul"},
#     {"nombre": "Sakamoto days","url":"https://www3.animeflv.net/anime/sakamoto-days"}
# ]

RUTA_CONFIG = "Multimedia/config.json"
categorias_peliculas = json.load(open(RUTA_CONFIG, "r", encoding="utf-8"))["categorias_peliculas"]
lista_animes = json.load(open(RUTA_CONFIG, "r", encoding="utf-8"))["lista_animes"]


gestor = GestorDescargas()


def obtener_nombres_animes():
    return [cat["nombre"] for cat in lista_animes]



def buscar_episodios(nombre_anime):
    """Busca la categoría y devuelve la URL para demostrar funcionamiento."""
    for cat in lista_animes:
        yield barra_html(0), "Empezando búsqueda..."
        if cat["nombre"] == nombre_anime:
            # Aquí puedes poner el proceso que quieras que se ejecute con la URL
            progreso = gestor.descargar_anime_con_progreso(cat['url'], nombre_anime)
            for porcentaje,mensaje in progreso:
                yield barra_html(porcentaje), mensaje
            break
        else:
            yield barra_html(0), "Categoría no encontrada."
    else:
        yield barra_html(0), "Categoría no encontrada."


def agregar_anime(url):
    """Agrega nueva anime a la lista y devuelve mensaje + lista actualizada."""
    # validar que no exista ya
    existente = next((cat for cat in lista_animes if cat["url"] == url), None)
    if existente:
        return f"El anime ya existe.", gr.Dropdown(choices=obtener_nombres_animes(), value=existente["nombre"])
    
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return "URL no válida.", gr.Dropdown(choices=obtener_nombres_animes(),value=None)
    
    nombre = gestor.obtener_nombre_anime_desde_url(url)
    if not nombre:
        return "No se pudo obtener el nombre del anime desde la URL.", gr.Dropdown(choices=obtener_nombres_animes(),value=None)
    lista_animes.append({"nombre": nombre, "url": url})
    # Guardar en config.json
    with open(RUTA_CONFIG, "r+", encoding="utf-8") as f:
        config = json.load(f)
        config["lista_animes"] = lista_animes
        f.seek(0)
        json.dump(config, f, indent=4, ensure_ascii=False)
        f.truncate()
    return f"Anime: '{nombre}' agregada correctamente.", gr.Dropdown(choices=obtener_nombres_animes(),value=nombre)



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
    if not categoria or categoria not in categorias_peliculas:
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
    with gr.Tab("🎬 Película"):
        gr.Markdown("## 🎬 Descargar película")

        categoria = gr.Dropdown(choices=categorias_peliculas, label="Categoría")
        link = gr.Textbox(label="Link de la película")
        nombre = gr.Textbox(label="Nombre del archivo (incluye extensión)")

        barra_progreso_peliculas = gr.HTML()
        salida = gr.Textbox(label="Estado", interactive=False)

        boton_descargar = gr.Button("Descargar")
        boton_descargar.click(fn=descargar, inputs=[categoria, link, nombre], outputs=[barra_progreso_peliculas, salida])
    
    with gr.Tab("🗾 Animes"):
        gr.Markdown("## 🗾 Descargar Animes de FLV")
        with gr.Tab("Buscar episodios nuevos"):
            dropdown_cat = gr.Dropdown(
                label="Selecciona un anime",
                choices=obtener_nombres_animes(),
                value=obtener_nombres_animes()[0] if obtener_nombres_animes() else None,
                interactive=True
            )
            btn_ejecutar = gr.Button("Buscar nuevos episodios")
            barra_progreso_anime = gr.HTML()
            salida_proceso = gr.Markdown("Proceso...")
            
            btn_ejecutar.click(
                buscar_episodios,
                inputs=dropdown_cat,
                outputs={barra_progreso_anime,salida_proceso}
            )
            
        with gr.Tab("Agregar nuevo anime"):
            url_input = gr.Textbox(label="URL del anime en AnimeFLV")
            btn_guardar = gr.Button("Guardar anime (NO DESCARGA)")
            salida_guardar = gr.Textbox(label="Estado")
            
            # Al guardar, se actualiza también el dropdown de la otra pestaña
            btn_guardar.click(
                agregar_anime,
                inputs=[url_input],
                outputs=[salida_guardar, dropdown_cat]
        )

demo.launch(server_name="0.0.0.0", server_port=8002, share=True)
