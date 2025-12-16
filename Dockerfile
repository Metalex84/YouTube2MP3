# YouTube to MP3 Downloader - Docker Container (Web Interface)
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app.py .
COPY descargar_audio.py .
COPY .env .
COPY templates/ templates/
COPY static/ static/
COPY README.md .

# Crear directorios para las descargas y logs
RUN mkdir -p /app/downloads /app/logs

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV DOWNLOAD_DIR=/app/downloads
ENV LOGS_DIR=/app/logs

# Usuario no root para seguridad
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Puerto expuesto para la aplicación web
EXPOSE 5000

# Punto de entrada para la aplicación web Flask
CMD ["python", "app.py"]
