# YouTube to MP3 Converter - Web Interface

Una aplicación web moderna con interfaz gráfica que descarga audio de videos de YouTube y los convierte a formato MP3.

> **Nota**: Este es el repositorio de la **aplicación web**. Si buscas la versión de línea de comandos (CLI), visita [YouTube2MP3_CLI](https://github.com/Metalex84/YouTube2MP3_CLI).

## 🌟 Características

- ✅ **Interfaz Web Moderna** - UI intuitiva con actualizaciones en tiempo real
- ✅ **Descarga audio de alta calidad** (320 kbps)
- ✅ **Convierte automáticamente a MP3**
- ✅ **Procesamiento en lote** - Sube archivos CSV o ingresa múltiples URLs
- ✅ **Actualizaciones en tiempo real** - Progreso de descarga vía WebSockets
- ✅ **API REST** - Para integración con otras aplicaciones
- ✅ **Descarga por lotes en ZIP** - Descarga todos los archivos en un solo ZIP
- ✅ **Soporte Docker** - Despliega fácilmente con Docker Compose
- ✅ **Cloud-ready** - Configurado para Render, Heroku, y otros servicios cloud
- ✅ **Manejo de errores robusto**

## 🐳 Docker (Opción más fácil)

¿Quieres la forma más rápida de empezar? Usa Docker:

### Opción 1: Scripts Wrapper (Recomendado)

**Windows (PowerShell):**
```powershell
.\run-web.ps1
```

**Linux/Mac (Bash):**
```bash
./run-web.sh
```

Estos scripts automáticamente:
- ✅ Construyen la imagen Docker si no existe
- ✅ Crean directorios necesarios (downloads, logs)
- ✅ Ejecutan el contenedor con la configuración correcta
- ✅ Muestran la URL para acceder a la aplicación

**Comandos adicionales:**
```bash
# Ver logs en tiempo real
./run-web.sh --logs

# Detener la aplicación
./run-web.sh --stop

# Forzar reconstrucción
./run-web.sh --build

# Cambiar puerto (default: 5000)
./run-web.sh --port 8080

# Limpiar todo (contenedor e imagen)
./run-web.sh --clean
```

### Opción 2: Docker Compose

```bash
# 1. Construir y ejecutar
docker-compose up -d

# 2. Acceder a la interfaz web
# Abre http://localhost:5000 en tu navegador
```

**Ventajas de Docker:**
- ✅ No necesitas instalar Python, FFmpeg ni dependencias
- ✅ Funciona en Windows, Mac y Linux
- ✅ Incluye interfaz web completa
- ✅ Configuración en un solo comando

**Documentación completa:**
- [DOCKER-QUICKSTART.md](DOCKER-QUICKSTART.md) - Guía rápida de Docker
- [DOCKER_OPTIMIZATION.md](DOCKER_OPTIMIZATION.md) - Optimizaciones de Docker

## ☁️ Despliegue en la Nube (Cloud Deployment)

¿Quieres que tu aplicación esté disponible en internet 24/7?

**Despliegue en Render (Recomendado):**
- ✅ Soporte completo para WebSockets
- ✅ Instalación fácil de FFmpeg
- ✅ Tier gratuito disponible
- ✅ Configuración con un clic usando `render.yaml`

**Guía completa:**
- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía paso a paso para desplegar en Render

**Inicio rápido:**
```bash
# 1. Push tu código a GitHub/GitLab/Bitbucket
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Ve a Render.com → New + → Blueprint
# 3. Conecta tu repositorio
# 4. ¡Deploy automático!
```

**Otras opciones de deployment:**
- [NAS-DEPLOYMENT.md](NAS-DEPLOYMENT.md) - Guía para desplegar en NAS (Synology, QNAP, etc.)

## Requisitos

- Python 3.7+
- FFmpeg (debe estar instalado en el sistema y disponible en PATH)
- Dependencias Python (ver requirements.txt)

## Instalación Local

### Instalación Manual

1. **Clona o descarga este repositorio**

2. **Instala FFmpeg** desde [ffmpeg.org](https://ffmpeg.org/download.html)

3. **Crea un entorno virtual**:
   ```bash
   python -m venv venv
   ```

4. **Activa el entorno virtual**:
   ```bash
   # Windows PowerShell
   venv\Scripts\Activate.ps1
   
   # Windows CMD
   venv\Scripts\activate.bat
   
   # Linux/Mac
   source venv/bin/activate
   ```

5. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

6. **Ejecuta la aplicación**:
   ```bash
   python app.py
   ```

7. **Abre tu navegador** en `http://localhost:5000`

## Uso

### Interfaz Web

1. Abre `http://localhost:5000` en tu navegador
2. Ingresa la URL del video de YouTube
3. Haz clic en "Descargar"
4. Espera a que se complete la descarga
5. Descarga el archivo MP3 generado

### Procesamiento en Lote

**Opción 1: Subir archivo CSV**
1. Prepara un archivo CSV con URLs (una por línea)
2. En la interfaz web, sube el archivo CSV
3. Las descargas comenzarán automáticamente
4. Descarga todos los archivos en un ZIP al finalizar

**Opción 2: Múltiples URLs en la interfaz**
1. Ingresa múltiples URLs separadas por líneas
2. Haz clic en "Descargar Lote"
3. Descarga el ZIP con todos los archivos

### API REST

La aplicación expone una API REST para integración:

**Iniciar descarga:**
```bash
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

**Consultar estado:**
```bash
curl http://localhost:5000/api/download/DOWNLOAD_ID
```

**Descargar archivo:**
```bash
curl http://localhost:5000/api/download/DOWNLOAD_ID/file -o audio.mp3
```

**Procesamiento en lote:**
```bash
curl -X POST http://localhost:5000/api/batch-download \
  -H "Content-Type: application/json" \
  -d '{"urls": ["URL1", "URL2", "URL3"]}'
```

**Health check:**
```bash
curl http://localhost:5000/api/health
```

## Configuración

### Variables de Entorno

Puedes configurar la aplicación usando variables de entorno o un archivo `.env`:

```env
# Puerto del servidor (default: 5000)
PORT=5000

# Directorio de descargas (default: ./downloads)
DOWNLOAD_DIR=/app/downloads

# Directorio de logs (default: ./logs)
LOGS_DIR=/app/logs

# Clave secreta de Flask (genera una para producción)
SECRET_KEY=your-secret-key-here

# Ubicación de FFmpeg (opcional, si no está en PATH)
FFMPEG_LOCATION=/path/to/ffmpeg/bin
```

### Configuración para Producción

Para producción, usa un servidor WSGI como Gunicorn:

```bash
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

La aplicación incluye configuraciones para:
- **Apache** (ver `apache-config/`)
- **Nginx** (ver `nginx-config/`)
- **Systemd** (ver `systemd/`)
- **Render** (ver `render.yaml`)
- **Heroku** (ver `Procfile`)

## Arquitectura

```
y2m-web/
├── app.py                  # Aplicación Flask principal
├── descargar_audio.py      # Módulo de descarga/conversión
├── wsgi.py                 # Entry point WSGI
├── requirements.txt        # Dependencias Python
├── Dockerfile              # Dockerfile para desarrollo
├── Dockerfile.production   # Dockerfile optimizado para producción
├── docker-compose.yml      # Configuración Docker Compose
├── render.yaml             # Configuración para Render.com
├── Procfile                # Configuración para Heroku
├── templates/              # Templates HTML
│   └── index.html
├── static/                 # Archivos estáticos
│   ├── style.css
│   └── script.js
├── apache-config/          # Configuración Apache
├── nginx-config/           # Configuración Nginx
└── systemd/                # Configuración Systemd
```

## Características Técnicas

### Backend
- **Flask**: Framework web minimalista
- **Flask-SocketIO**: WebSockets para actualizaciones en tiempo real
- **yt-dlp**: Motor de descarga de YouTube
- **FFmpeg**: Conversión de audio a MP3

### Frontend
- **HTML5/CSS3**: Interfaz moderna y responsive
- **JavaScript Vanilla**: Sin frameworks pesados
- **Socket.IO**: Cliente WebSocket para actualizaciones en tiempo real

### Deployment
- **Docker**: Contenedorización completa
- **Gunicorn + Eventlet**: Servidor WSGI con soporte WebSocket
- **Cloud-ready**: Configurado para múltiples plataformas cloud

## Solución de problemas

### Error: "FFmpeg not found"
- Instala FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html)
- Asegúrate de que FFmpeg esté en el PATH
- O configura la variable `FFMPEG_LOCATION`

### Error de WebSocket
- Asegúrate de que el puerto 5000 no esté bloqueado
- Verifica que Flask-SocketIO esté instalado correctamente
- En producción, usa Gunicorn con `--worker-class eventlet`

### Error de descarga
- Verifica que la URL del video sea correcta
- Algunos videos pueden estar restringidos
- Verifica tu conexión a internet

### Problemas de permisos
- Asegúrate de que los directorios `downloads/` y `logs/` tengan permisos de escritura
- En Docker, el usuario `appuser` debe tener permisos

## Relacionado

- **CLI Version**: [y2m-cli](../y2m-cli) - Versión de línea de comandos

## Licencia

Este proyecto es de código abierto. Úsalo responsablemente y respeta los términos de servicio de YouTube.
