import platform
import os
import subprocess

class GestorDescargas:
    def __init__(self):
        # Dentro del contenedor siempre será Linux
        self.ruta_base = "/mnt/Multimedia"

    def descargar_pelicula(self, categoria, url, nombre):
        ruta_categoria = os.path.join(self.ruta_base, "Peliculas", categoria)
        os.makedirs(ruta_categoria, exist_ok=True)

        ruta_archivo = os.path.join(ruta_categoria, nombre)
        comando = ["wget", url, "-O", ruta_archivo]

        try:
            subprocess.run(comando, check=True)
            return f"✅ Película descargada en: {ruta_archivo}"
        except subprocess.CalledProcessError as e:
            return f"❌ Error al descargar: {e}"