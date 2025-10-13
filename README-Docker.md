# YouTube to MP3 Downloader - Docker Edition 🐳

Esta es la versión containerizada del YouTube to MP3 Downloader, que permite ejecutar la aplicación en cualquier máquina que tenga Docker instalado, sin necesidad de configurar Python, FFmpeg o dependencias.

## 🚀 Inicio Rápido

### Prerrequisitos
- Docker instalado en tu sistema
- Para Windows: PowerShell 5.0+
- Para Linux/Mac: Bash

### 1. Construir la imagen Docker

**Windows (PowerShell):**
```powershell
.\docker-run.ps1 build
```

**Linux/Mac (Bash):**
```bash
chmod +x docker-run.sh
./docker-run.sh build
```

### 2. Ejecutar el contenedor

**Descargar una URL:**
```powershell
# Windows
.\docker-run.ps1 run "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Linux/Mac
./docker-run.sh run "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

**Procesar archivo CSV:**
```powershell
# Primero crea un archivo urls.csv en el directorio actual
# Windows
.\docker-run.ps1 run --csv-file urls.csv --max-concurrent 3

# Linux/Mac
./docker-run.sh run --csv-file urls.csv --max-concurrent 3
```

## 📁 Estructura de Directorios

Cuando ejecutes el contenedor, se crearán automáticamente estos directorios:

```
proyecto/
├── downloads/          # Los archivos MP3 descargados aparecerán aquí
├── logs/              # Los archivos de log se guardan aquí
├── urls.csv           # (Opcional) Tu archivo con URLs
├── docker-run.ps1     # Script para Windows
├── docker-run.sh      # Script para Linux/Mac
└── Dockerfile         # Configuración del contenedor
```

## 🔧 Comandos Disponibles

### Windows (PowerShell)

| Comando | Descripción |
|---------|-------------|
| `.\docker-run.ps1 build` | Construir la imagen Docker |
| `.\docker-run.ps1 run [args]` | Ejecutar con argumentos |
| `.\docker-run.ps1 shell` | Abrir shell interactiva |
| `.\docker-run.ps1 logs` | Mostrar logs en tiempo real |
| `.\docker-run.ps1 clean` | Limpiar imágenes y contenedores |

### Linux/Mac (Bash)

| Comando | Descripción |
|---------|-------------|
| `./docker-run.sh build` | Construir la imagen Docker |
| `./docker-run.sh run [args]` | Ejecutar con argumentos |
| `./docker-run.sh shell` | Abrir shell interactiva |
| `./docker-run.sh logs` | Mostrar logs en tiempo real |
| `./docker-run.sh clean` | Limpiar imágenes y contenedores |

## 📝 Ejemplos Prácticos

### Descargar una canción
```bash
.\docker-run.ps1 run "https://youtube.com/watch?v=VIDEO_ID"
```

### Procesar múltiples URLs con límite de concurrencia
```bash
.\docker-run.ps1 run --csv-file urls.csv --max-concurrent 2
```

### Ver la versión
```bash
.\docker-run.ps1 run --version
```

### Especificar directorio de salida personalizado
```bash
.\docker-run.ps1 run -o downloads "https://youtube.com/watch?v=VIDEO_ID"
```

### Abrir shell para debugging
```bash
.\docker-run.ps1 shell
# Dentro del contenedor puedes ejecutar:
# python descargar_audio.py --help
# ls -la downloads/
```

## 🔍 Monitoreo y Logs

### Ver logs en tiempo real
```bash
.\docker-run.ps1 logs
```

Los logs se almacenan en `./logs/youtube_downloader.log` y contienen:
- Timestamps de todas las operaciones
- Detalles de cada descarga
- Mensajes de error y warnings
- Estadísticas de la sesión

## 🐳 Usando Docker Compose (Alternativa)

Si prefieres usar Docker Compose:

```bash
# Construir y ejecutar
docker-compose run --rm youtube-mp3 --version

# Con archivo CSV
docker-compose run --rm youtube-mp3 --csv-file urls.csv

# Con URL específica
docker-compose run --rm youtube-mp3 "https://youtube.com/watch?v=VIDEO_ID"
```

## 🛠️ Personalización

### Modificar recursos del contenedor
Edita `docker-compose.yml` para ajustar memoria y CPU:
```yaml
deploy:
  resources:
    limits:
      memory: 1G      # Aumentar memoria
      cpus: '2.0'     # Usar 2 CPUs
```

### Agregar variables de entorno
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - CUSTOM_VAR=value
```

## 🔧 Troubleshooting

### Error: "Docker no está instalado"
- Instala Docker Desktop desde https://docker.com/products/docker-desktop
- Asegúrate de que Docker esté en el PATH

### Error de permisos en Linux/Mac
```bash
chmod +x docker-run.sh
```

### Limpiar todo y empezar de nuevo
```bash
.\docker-run.ps1 clean
.\docker-run.ps1 build
```

### Verificar que la imagen se construyó correctamente
```bash
docker images | grep youtube-mp3
```

## 🌟 Ventajas de la Versión Docker

- ✅ **No necesitas instalar Python o FFmpeg** - Todo está en el contenedor
- ✅ **Ejecuta en cualquier sistema** - Windows, Mac, Linux
- ✅ **Aislamiento completo** - No afecta tu sistema
- ✅ **Fácil distribución** - Solo comparte el directorio del proyecto
- ✅ **Logs persistentes** - Se mantienen fuera del contenedor
- ✅ **Descargas persistentes** - Los MP3 se guardan en tu sistema
- ✅ **Limpieza automática** - Los contenedores se eliminan tras la ejecución

## 📖 Más Información

Para más detalles sobre los argumentos de la aplicación, ejecuta:
```bash
.\docker-run.ps1 run --help
```