import re
from urllib.parse import urlparse

def validar_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)

def limpiar_nombre_archivo(name: str):
    if not isinstance(name, str):
        return None
    name = name.strip()
    if "." in name:
        name = name.rsplit(".", 1)[0]
    pattern = re.compile(r'^[\w\-\s\(\)]+([A-Za-z0-9]{1,10})$')
    if not pattern.match(name):
        return None
    return name