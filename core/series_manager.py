from utils.validators import validar_url, limpiar_nombre_archivo
from ui.components import barra_html
import json

def descargar_serie(json_serie, gestor):
    json_serie = json.loads(json_serie)
    yield barra_html(0), "Empezando descarga..."
    progreso = gestor.descargar_serie_con_progreso(json_serie)
    for porcentaje, mensaje in progreso:
        yield barra_html(porcentaje), mensaje
    gestor.descargar_serie_con_progreso(json_serie)