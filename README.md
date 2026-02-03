# YouTube to MP3 Converter

Un script en Python que descarga audio de videos de YouTube y los convierte a formato MP3.

## 🌟 Características

- ✅ **Interfaz Web Moderna** (branch `web`) - UI intuitiva con actualizaciones en tiempo real
- ✅ **Descarga audio de alta calidad** (320 kbps)
- ✅ **Convierte automáticamente a MP3**
- ✅ **Procesamiento en lote desde archivo CSV**
- ✅ **Soporte Docker** - Ejecuta sin instalar dependencias
- ✅ Limpia nombres de archivo problemáticos
- ✅ Muestra progreso de descarga en tiempo real
- ✅ Interfaz de línea de comandos mejorada
- ✅ API REST para integración
- ✅ Manejo de errores robusto
- ✅ Resumen detallado de procesamiento

## 🐳 Docker (Opción más fácil)

¿Quieres la forma más rápida de empezar? Usa Docker:

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

## Requisitos

- Python 3.7+
- FFmpeg (debe estar instalado en el sistema y disponible en PATH)
- yt-dlp (incluido en requirements.txt)

## Instalación

### 🚀 Configuración Automática (Recomendado)

El proyecto incluye un script de configuración automático que se encarga de todo:

1. **Descarga el proyecto** a tu ordenador
2. **Abre PowerShell como administrador** (clic derecho → "Ejecutar como administrador")
3. **Navega al directorio del proyecto**:
   ```powershell
   cd "C:\ruta\a\tu\proyecto\y2m"
   ```
4. **Ejecuta la configuración automática**:
   ```powershell
   # Opción 1: PowerShell (más completo, instala Python/FFmpeg automáticamente)
   .\configurar.ps1
   
   # Opción 2: Batch (más compatible, requiere Python pre-instalado)
   configurar.bat
   ```

Este script automáticamente:
- ✅ Verifica e instala Python 3.11.9 si es necesario
- ✅ Verifica e instala FFmpeg si es necesario  
- ✅ Crea el entorno virtual
- ✅ Instala todas las dependencias
- ✅ Verifica que todo funciona correctamente

### 🔧 Configuración Manual (Alternativa)

Si prefieres configurar manualmente:

1. Instala Python 3.7+ desde [python.org](https://www.python.org/downloads/)
2. Instala FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html)
3. Clona o descarga este repositorio
4. Activa el entorno virtual:
   ```bash
   venv\Scripts\Activate.ps1  # Windows PowerShell
   # o
   venv\Scripts\activate.bat  # Windows CMD
   ```
5. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

### 🎯 Uso Simplificado (Recomendado)

Después de la configuración automática, usa el script ejecutor:

**Descargar una URL:**
```batch
# Usando archivo .bat (más compatible)
ejecutar.bat "https://www.youtube.com/watch?v=VIDEO_ID"

# O usando PowerShell
.\ejecutar.ps1 "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Especificar directorio de salida:**
```batch
ejecutar.bat -o "C:\Mi\Carpeta\Musica" "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Procesamiento en lote desde CSV:**
```batch
ejecutar.bat --csv-file urls.csv
```

**CSV con directorio personalizado:**
```batch
ejecutar.bat --csv-file urls.csv -o "C:\Mi\Carpeta\Musica"
```

**Modo interactivo:**
```batch
ejecutar.bat
# El script te pedirá que pegues la URL
```

**Ver ayuda detallada:**
```batch
ejecutar.bat --help
```

### 🔧 Uso Manual (Si no usas el ejecutor)

**Activar entorno virtual primero:**
```powershell
venv\Scripts\Activate.ps1
```

**Luego usar el script Python directamente:**
```bash
python descargar_audio.py "https://www.youtube.com/watch?v=VIDEO_ID"
python descargar_audio.py --csv-file urls.csv
python descargar_audio.py -o "C:\Mi\Musica" "https://..."
```

### Opciones disponibles
- `-h, --help`: Muestra ayuda
- `-o, --output-dir`: Especifica directorio de salida
- `--csv-file`: Procesa URLs desde archivo CSV
- `--version`: Muestra versión del programa

## Formato del archivo CSV

El archivo CSV debe contener las URLs de YouTube, una por fila. Puede incluir un encabezado opcional:

```csv
URL
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

O sin encabezado:

```csv
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

### Características del procesamiento CSV:
- ✅ Detecta automáticamente si hay encabezados
- ✅ Ignora líneas vacías
- ✅ Valida cada URL antes de procesar
- ✅ Muestra progreso detallado para cada descarga
- ✅ Resumen final con estadísticas
- ✅ Manejo de interrupciones (Ctrl+C) con resumen parcial

## Scripts Incluidos

### 🛠️ Configuradores

**configurar.ps1** - Configuración avanzada (PowerShell)
```powershell
.\configurar.ps1              # Configuración completa con instalación automática
.\configurar.ps1 -SkipFFmpeg  # Omitir instalación de FFmpeg
```

**configurar.bat** - Configuración simple (Batch)
```batch
configurar.bat                # Configuración básica (requiere Python pre-instalado)
```

### 🚀 Ejecutores

**ejecutar.bat** - Ejecutor principal (Recomendado)
```batch
ejecutar.bat [opciones]       # Ejecuta el programa
```

**ejecutar.ps1** - Ejecutor PowerShell (Alternativo)
```powershell
.\ejecutar.ps1 [opciones]     # Ejecuta el programa
.\ejecutar.ps1 help          # Muestra ayuda rápida
```

### 🎥 Herramientas adicionales

**instalar_ffmpeg.ps1** - Instalador de FFmpeg
```powershell
.\instalar_ffmpeg.ps1        # Instala sólo FFmpeg
```

## Solución de problemas

### 🚑 Configuración

**Error: "Python no está instalado"**
- Ejecuta `.\configurar.ps1` como administrador
- O instala Python manualmente desde [python.org](https://www.python.org/downloads/)

**Error: "FFmpeg not found"**
- Ejecuta `.\instalar_ffmpeg.ps1`
- O ejecuta `.\configurar.ps1` de nuevo
- O instala FFmpeg manualmente desde [ffmpeg.org](https://ffmpeg.org/download.html)

**Error: "No se encontró el entorno virtual"**
- Ejecuta `.\configurar.ps1` para crear el entorno
- Asegúrate de estar en el directorio correcto del proyecto

### 📱 Ejecución

**Error de descarga**
- Verifica que la URL del video sea correcta
- Asegúrate de tener conexión a internet
- Algunos videos pueden estar restringidos por región o privados
- Prueba con una URL diferente

**Caracteres especiales en nombres de archivo**
- El script limpia automáticamente los caracteres problemáticos
- Los archivos se guardan con nombres seguros para el sistema de archivos

**Error: "Execution Policy"**
- Ejecuta: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- O ejecuta: `PowerShell -ExecutionPolicy Bypass -File .\configurar.ps1`

### 📝 CSV

**El archivo CSV no se procesa correctamente**
- Verifica que el archivo tenga URLs válidas (que empiecen con http:// o https://)
- Asegúrate de que no haya líneas vacías extra
- El formato debe ser una URL por línea

## Licencia

Este proyecto es de código abierto. Úsalo responsablemente y respeta los términos de servicio de YouTube.