import json

def guardar_config(ruta_config, clave, valor):
    with open(ruta_config, "r+", encoding="utf-8") as f:
        config = json.load(f)
        config[clave] = valor
        f.seek(0)
        json.dump(config, f, indent=4, ensure_ascii=False)
        f.truncate()