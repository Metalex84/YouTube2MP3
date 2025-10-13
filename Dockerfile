# YouTube to MP3 Downloader - Docker Container
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
COPY descargar_audio.py .
COPY README.md .

# Crear directorio para las descargas
RUN mkdir -p /app/downloads /app/logs

# Configurar variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Usuario no root para seguridad
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Puerto expuesto (por si queremos añadir API web en el futuro)
EXPOSE 8080

# Punto de entrada
ENTRYPOINT ["python", "descargar_audio.py"]

# Comando por defecto (mostrar ayuda)
CMD ["--help"]