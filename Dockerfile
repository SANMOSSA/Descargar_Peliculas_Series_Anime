FROM python:3.11

# Instalar dependencias de sistema necesarias para Chromium en Playwright
RUN apt-get update && apt-get install -y \
    wget \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libasound2 \
    libxcomposite1 \
    libxrandr2 \
    libgbm1 \
    libxdamage1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar el código dentro del contenedor
COPY . .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Chromium para Playwright dentro del contenedor
RUN playwright install --with-deps chromium

# Crear carpeta de destino para las películas dentro del contenedor
RUN mkdir -p /Multimedia/Peliculas

# Exponer puerto para Gradio
EXPOSE 8002

# Comando para iniciar la app
CMD ["python", "app.py"]