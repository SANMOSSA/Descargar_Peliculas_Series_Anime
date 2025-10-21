FROM python:3.11

# Instalar wget para las descargas
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar el código dentro del contenedor
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Crear carpeta de destino para las películas dentro del contenedor
RUN mkdir -p /mnt/Multimedia/Peliculas

# Exponer puerto para Gradio
EXPOSE 8002

# Comando para iniciar la app
CMD ["python", "app.py"]