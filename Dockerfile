FROM python:3.11

# Instalar dependencias de sistema necesarias para Chromium en Playwright
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*


# Crear directorio de trabajo
WORKDIR /app

# Copiar el código dentro del contenedor
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Chromium para Playwright dentro del contenedor
RUN playwright install-deps
RUN playwright install chromium

# Crear carpeta de destino para las películas dentro del contenedor
RUN mkdir -p /Multimedia/Peliculas
RUN mkdir -p /Multimedia/Animes
# Exponer puerto para Gradio
EXPOSE 8002

# Comando para iniciar la app
CMD ["python", "app.py"]