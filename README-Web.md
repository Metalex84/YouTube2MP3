# YouTube2MP3 - Web Interface

Una interfaz web moderna y amigable para el convertidor YouTube to MP3.

## 🌟 Características

- ✅ **Interfaz Web Moderna** - UI intuitiva con diseño responsive
- ✅ **Descarga Simple** - Convierte una URL de YouTube a MP3
- ✅ **Descarga en Lote** - Procesa múltiples URLs desde CSV o lista
- ✅ **Progreso en Tiempo Real** - Actualización de progreso vía WebSocket
- ✅ **API RESTful** - Endpoints para integración con otras aplicaciones
- ✅ **Descarga Directa** - Descarga los MP3 directamente desde el navegador

## 📋 Requisitos Previos

Antes de ejecutar la interfaz web, asegúrate de tener:

1. **Python 3.7+** instalado
2. **FFmpeg** instalado y disponible en PATH
3. **Todas las dependencias** del proyecto base (ver README.md principal)

## 🚀 Instalación Rápida

### 1. Instalar Dependencias Web

Si ya configuraste el proyecto base, solo necesitas instalar las dependencias web adicionales:

```powershell
# Activar el entorno virtual
.\venv\Scripts\Activate.ps1

# Instalar dependencias web
pip install -r requirements.txt
```

### 2. Iniciar el Servidor Web

```powershell
# Opción 1: Ejecutar directamente
python app.py

# Opción 2: Con configuración específica
$env:DOWNLOAD_DIR="C:\Mi\Carpeta\Descargas"
python app.py
```

### 3. Acceder a la Interfaz Web

Abre tu navegador y visita:
```
http://localhost:5000
```

## 📖 Uso de la Interfaz Web

### Descarga Simple

1. Selecciona la pestaña **"📎 Descarga Simple"**
2. Pega la URL del video de YouTube
3. Haz clic en **"🚀 Descargar"**
4. Observa el progreso en tiempo real
5. Cuando termine, haz clic en **"📥 Descargar MP3"**

### Descarga en Lote - Subir CSV

1. Selecciona la pestaña **"📋 Descarga en Lote"**
2. Haz clic en **"📁 Seleccionar archivo CSV"**
3. Selecciona tu archivo CSV con las URLs
4. Haz clic en **"🚀 Subir y Procesar"**
5. Observa el progreso de todas las descargas

**Formato del CSV:**
```csv
URL
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

### Descarga en Lote - Pegar URLs

1. Selecciona la pestaña **"📋 Descarga en Lote"**
2. En el área de texto, pega las URLs (una por línea)
3. Haz clic en **"🚀 Procesar URLs"**
4. Observa el progreso de todas las descargas

**Ejemplo:**
```
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

## 🔌 API REST

La aplicación web incluye una API REST completa para integración programática.

### Endpoints Disponibles

#### 1. Health Check
```http
GET /api/health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "downloads_dir": "C:\\path\\to\\downloads"
}
```

#### 2. Iniciar Descarga Simple
```http
POST /api/download
Content-Type: application/json

{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Respuesta:**
```json
{
  "success": true,
  "download_id": "uuid-here",
  "message": "Download started"
}
```

#### 3. Iniciar Descarga en Lote (JSON)
```http
POST /api/batch-download
Content-Type: application/json

{
  "urls": [
    "https://www.youtube.com/watch?v=VIDEO_ID_1",
    "https://www.youtube.com/watch?v=VIDEO_ID_2"
  ]
}
```

**Respuesta:**
```json
{
  "success": true,
  "download_ids": ["uuid-1", "uuid-2"],
  "count": 2,
  "message": "Started 2 downloads"
}
```

#### 4. Iniciar Descarga en Lote (CSV)
```http
POST /api/batch-download
Content-Type: multipart/form-data

file: [archivo CSV]
```

#### 5. Listar Todas las Descargas
```http
GET /api/downloads
```

**Respuesta:**
```json
{
  "downloads": [
    {
      "id": "uuid",
      "url": "https://...",
      "status": "completed",
      "title": "Video Title",
      "filename": "Video Title.mp3",
      "created_at": "2025-11-16T10:00:00"
    }
  ]
}
```

#### 6. Estado de una Descarga Específica
```http
GET /api/download/{download_id}
```

**Respuesta:**
```json
{
  "id": "uuid",
  "url": "https://...",
  "status": "downloading",
  "title": "Video Title",
  "started_at": "2025-11-16T10:00:00"
}
```

**Estados posibles:**
- `pending` - En cola, esperando a iniciar
- `downloading` - Descargando actualmente
- `completed` - Completado exitosamente
- `failed` - Error durante la descarga

#### 7. Descargar Archivo MP3
```http
GET /api/download/{download_id}/file
```

Descarga directamente el archivo MP3.

### Ejemplo con cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Iniciar descarga
curl -X POST http://localhost:5000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Listar descargas
curl http://localhost:5000/api/downloads

# Descargar archivo
curl -O http://localhost:5000/api/download/{download_id}/file
```

### Ejemplo con Python

```python
import requests

# Iniciar descarga
response = requests.post('http://localhost:5000/api/download', 
                        json={'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'})
data = response.json()
download_id = data['download_id']

# Verificar estado
response = requests.get(f'http://localhost:5000/api/download/{download_id}')
status = response.json()
print(f"Estado: {status['status']}")

# Descargar archivo (cuando esté listo)
if status['status'] == 'completed':
    response = requests.get(f'http://localhost:5000/api/download/{download_id}/file')
    with open('audio.mp3', 'wb') as f:
        f.write(response.content)
```

## 🔄 WebSocket Events

La aplicación usa WebSocket para actualizaciones en tiempo real.

### Eventos del Servidor

#### `connected`
Emitido cuando el cliente se conecta.
```json
{
  "message": "Connected to YouTube2MP3 server"
}
```

#### `download_progress`
Emitido durante la descarga con actualizaciones de progreso.
```json
{
  "download_id": "uuid",
  "status": "downloading",
  "percent": "45.2%",
  "speed": "2.5MiB/s",
  "eta": "00:30"
}
```

#### `download_complete`
Emitido cuando una descarga termina exitosamente.
```json
{
  "download_id": "uuid",
  "title": "Video Title",
  "filename": "Video Title.mp3"
}
```

#### `download_error`
Emitido cuando una descarga falla.
```json
{
  "download_id": "uuid",
  "error": "Error message"
}
```

## ⚙️ Configuración

### Variables de Entorno

Puedes configurar el comportamiento de la aplicación con estas variables:

```powershell
# Directorio de descargas (por defecto: ./downloads)
$env:DOWNLOAD_DIR="C:\Mi\Carpeta\Descargas"

# Directorio de logs (por defecto: ./logs)
$env:LOGS_DIR="C:\Mi\Carpeta\Logs"

# Ejecutar la aplicación
python app.py
```

### Configuración del Servidor

En `app.py`, puedes modificar:

```python
# Puerto del servidor (por defecto: 5000)
socketio.run(app, host='0.0.0.0', port=5000)

# Tamaño máximo de archivo CSV (por defecto: 16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
```

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"

Asegúrate de instalar las dependencias:
```powershell
pip install -r requirements.txt
```

### Error: "Address already in use"

El puerto 5000 está ocupado. Cierra otras aplicaciones o cambia el puerto en `app.py`.

### Las descargas no aparecen en tiempo real

Verifica que WebSocket esté conectado (indicador verde en la esquina inferior derecha). Si aparece desconectado:
1. Recarga la página
2. Verifica la consola del navegador (F12) para errores
3. Asegúrate de que no haya firewall bloqueando la conexión

### Error: "FFmpeg not found"

FFmpeg debe estar instalado y disponible en PATH. Ejecuta:
```powershell
ffmpeg -version
```

Si no funciona, instala FFmpeg:
```powershell
.\instalar_ffmpeg.ps1
```

### Los archivos descargados no aparecen

Por defecto, los archivos se guardan en la carpeta `downloads` del proyecto. Verifica:
```powershell
ls .\downloads\
```

## 🚀 Despliegue en Producción

### Usando Gunicorn (Linux/Mac)

```bash
pip install gunicorn

gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

### Usando Waitress (Windows)

```powershell
pip install waitress

waitress-serve --listen=0.0.0.0:5000 app:app
```

### Con Docker

El proyecto incluye soporte para Docker (ver `README-Docker.md` y `Dockerfile`).

## 📁 Estructura del Proyecto Web

```
YouTube2MP3/
├── app.py                    # Aplicación Flask principal
├── descargar_audio.py        # Módulo de descarga (reutilizado)
├── requirements.txt          # Dependencias (incluye web)
├── templates/
│   └── index.html           # Interfaz web
├── static/
│   ├── style.css            # Estilos CSS
│   └── script.js            # JavaScript del cliente
└── downloads/               # Archivos MP3 descargados
```

## 🔐 Seguridad

**IMPORTANTE:** Esta aplicación es para uso personal/desarrollo. Para producción:

1. **Cambia la SECRET_KEY** en `app.py`
2. **Configura HTTPS** con un reverse proxy (nginx, Apache)
3. **Implementa autenticación** si es accesible públicamente
4. **Limita el rate limiting** para evitar abuso
5. **Valida entrada** de usuarios más rigurosamente

## 📄 Licencia

Este proyecto es de código abierto. Úsalo responsablemente y respeta los términos de servicio de YouTube.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras un bug o tienes una sugerencia:

1. Abre un issue en el repositorio
2. Crea un pull request con tus cambios
3. Asegúrate de seguir el estilo de código existente

## 📞 Soporte

Para problemas o preguntas:
- Revisa este documento y el README.md principal
- Verifica los logs en `./logs/youtube_downloader.log`
- Consulta la consola del navegador (F12) para errores del cliente

---

**¡Disfruta convirtiendo tus videos favoritos de YouTube a MP3! 🎵**
