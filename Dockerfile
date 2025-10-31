FROM python:3.11

# 📌 1. Instalar dependencias del sistema necesarias para Playwright/Chromium
RUN apt-get update && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*

# 📌 2. Crear directorio de trabajo
WORKDIR /app

# 📌 3. Copiar solo requirements.txt para cachear instalación de Python deps
COPY requirements.txt .

# 📌 4. Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# 📌 5. Instalar deps y navegadores de Playwright (solo cuando cambie requirements.txt)
RUN playwright install-deps && playwright install chromium

# 📌 6. Copiar SOLO ahora el resto del código (no rompe caché de deps)
COPY . .

# 📌 7. Crear carpetas multimedia
RUN mkdir -p /Multimedia/Peliculas && mkdir -p /Multimedia/Animes

# 📌 8. Exponer puerto
EXPOSE 8002

# 📌 9. Comando por defecto
CMD ["python", "app.py"]