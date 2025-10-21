import gradio as gr
from descargar import GestorDescargas

categorias_opciones = ["Accion", "Animacion", "Comedia", "Historia", "Romance", "Terror"]

gestor = GestorDescargas()

def descargar(categoria, link, nombre):
    return gestor.descargar_pelicula(categoria, link, nombre)

with gr.Blocks() as demo:
    gr.Markdown("## 🎬 Descargar película libre de derechos")
    
    categoria = gr.Dropdown(choices=categorias_opciones, label="Categoría")
    link = gr.Textbox(label="Link de la película")
    nombre = gr.Textbox(label="Nombre del archivo (incluye .mp4, .mkv, etc.)")
    
    boton_descargar = gr.Button("Descargar")
    salida = gr.Textbox(label="Resultado", interactive=False)
    
    boton_descargar.click(fn=descargar, inputs=[categoria, link, nombre], outputs=salida)

demo.launch(server_name="0.0.0.0", server_port=8002)


