import json

def guardar_config(ruta_config, clave, valor):
    with open(ruta_config, "r+", encoding="utf-8") as f:
        config = json.load(f)
        config[clave] = valor
        f.seek(0)
        json.dump(config, f, indent=4, ensure_ascii=False)
        f.truncate()

def crear_config_inicial(ruta_config):
    with open(ruta_config, "w", encoding="utf-8") as archivo_config:
        json.dump(
            {
                "categorias_peliculas": [
                    "Accion",
                    "Animacion",
                    "Comedia",
                    "Historia",
                    "Romance",
                    "Terror"
                ],
                "lista_animes": [
                ]
            },
            archivo_config,
            indent=4,
            ensure_ascii=False
        )