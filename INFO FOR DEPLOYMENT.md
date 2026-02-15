# Información de Despliegue - YouTube2MP3 Web

## ⚠️ IMPORTANTE: Limitación conocida

**Este proyecto NO funcionará en servidores de producción en la nube** (Render, Heroku, AWS, etc.) debido a que YouTube bloquea activamente el tráfico proveniente de direcciones IP de centros de datos.

---

## El Problema del Bloqueo de YouTube

### ¿Qué ocurre?

YouTube implementa sistemas de detección de bots que bloquean las peticiones provenientes de:

- **Rangos de IP de centros de datos** (AWS, Google Cloud, Azure, etc.)
- **Servicios de hosting** (Render, Heroku, DigitalOcean, etc.)
- **VPNs comerciales** y proxies conocidos

### Error típico

Cuando se intenta descargar desde un servidor de producción, yt-dlp falla con errores como:

```
ERROR: Sign in to confirm you're not a bot. This helps protect our community.
```

```
ERROR: Unable to extract video data. YouTube said: Sign in to confirm your age
```

```
HTTP Error 403: Forbidden
```

### ¿Por qué funciona en local pero no en producción?

| Entorno | IP | Resultado |
|---------|-----|-----------|
| Tu PC (desarrollo) | IP residencial | ✅ Funciona |
| Servidor Render/Heroku | IP de datacenter | ❌ Bloqueado |

YouTube mantiene listas actualizadas de rangos de IP de centros de datos y los bloquea preventivamente, incluso si las peticiones son legítimas.

### Intentos de solución que NO funcionan

1. **Cookies de sesión**: Aunque se implementó soporte para cookies en la versión de producción, YouTube invalida las sesiones cuando detecta uso desde IPs de datacenter.

2. **Cambiar User-Agent**: YouTube no se basa solo en el User-Agent para detectar bots.

3. **Añadir delays/throttling**: El bloqueo es por IP, no por frecuencia de peticiones.

4. **Proxies residenciales**: Funcionarían pero son caros y poco fiables.

---

## Diferencias entre Desarrollo y Producción

### Archivos que difieren

| Archivo | Diferencia principal |
|---------|---------------------|
| `app.py` | Múltiples cambios (ver detalle abajo) |
| `cookies.txt` | Solo existe en producción (intento de autenticación) |

### Diferencias en `app.py`

#### 1. Eventlet Monkey Patching (solo producción)

**Producción** (líneas 1-3):
```python
import eventlet
eventlet.monkey_patch()
```

**Desarrollo**: No tiene este patching.

> **Motivo**: Eventlet requiere monkey patching para funcionar correctamente con websockets en producción con Gunicorn.

#### 2. Modo asíncrono de SocketIO

**Producción**:
```python
socketio = SocketIO(app, async_mode='eventlet', ...)
```

**Desarrollo**:
```python
socketio = SocketIO(app, async_mode='threading', ...)
```

> **Motivo**: En desarrollo se usa threading (más simple); en producción se usa eventlet (más eficiente para websockets).

#### 3. Sistema de Cookies (solo producción)

**Producción** incluye la función `setup_cookies()` (líneas 87-114):
- Busca cookies en `/etc/secrets/cookies.txt` (Render secret files)
- Las copia a `/app/cookies.txt` (ubicación escribible)
- Las usa con yt-dlp para autenticación

**Desarrollo**: No tiene sistema de cookies.

> **Motivo**: Intento fallido de evadir el bloqueo de YouTube mediante autenticación.

#### 4. Configuración de yt-dlp

| Parámetro | Producción | Desarrollo |
|-----------|------------|------------|
| `format` | `'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best'` | `'bestaudio/best'` |
| `preferredquality` | `'192'` | `'320'` |
| `retries` | `5` | `3` |
| `player_client` | `['web', 'android']` | `['ios', 'android', 'web']` |
| `cookiefile` | Sí (si existe) | No |

> **Motivo**: La versión de producción tiene configuración más conservadora para intentar evitar bloqueos (menor calidad, más reintentos, formatos específicos).

#### 5. User-Agent

**Producción**:
```python
'User-Agent': 'Mozilla/5.0 ... Chrome/122.0.0.0 ...'
```

**Desarrollo**:
```python
'User-Agent': 'Mozilla/5.0 ... Chrome/120.0.0.0 ...'
```

---

## Archivos exclusivos de cada versión

### Solo en Producción (`y2m_web_production/`)

- `cookies.txt` - Archivo de cookies para autenticación YouTube (no funciona)

### Solo en Desarrollo (`y2m_web/`)

- Ninguno relevante

---

## Instrucciones de Despliegue

### ❌ NO desplegar en servicios cloud

Este proyecto **no debe desplegarse** en:
- Render
- Heroku
- Railway
- Fly.io
- AWS/GCP/Azure
- Cualquier hosting con IP de datacenter

### ✅ Entornos donde SÍ funciona

1. **Servidor local/doméstico** con IP residencial
2. **NAS personal** (Synology, QNAP, etc.)
3. **Raspberry Pi** en red doméstica
4. **VPS con IP residencial** (muy raro y caro)

### Despliegue en servidor local/NAS

Ver el archivo `NAS-DEPLOYMENT.md` para instrucciones detalladas.

Resumen rápido:

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd y2m_web

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Instalar FFmpeg
# En Ubuntu/Debian:
sudo apt install ffmpeg
# En Windows: descargar de ffmpeg.org

# 4. Ejecutar (desarrollo)
python app.py

# 5. Ejecutar (producción local)
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 app:app
```

### Usando Docker (local)

```bash
docker-compose up -d
```

---

## Recomendación Final

**Usa la versión de desarrollo (`y2m_web/`)** para ejecutar en tu red local. La versión de producción (`y2m_web_production/`) contiene optimizaciones y workarounds que no son necesarios cuando se ejecuta desde una IP residencial.

Si necesitas acceso remoto, considera:
- **Tailscale/ZeroTier**: VPN para acceder a tu servidor local desde cualquier lugar
- **Cloudflare Tunnel**: Exponer tu servidor local de forma segura (pero el tráfico de descarga sigue saliendo desde tu IP residencial)

---

## Historial de intentos de solución

1. ✅ Eventlet para websockets → Funcionó
2. ✅ FFmpeg en container → Funcionó
3. ❌ Cookies de autenticación → No evita el bloqueo
4. ❌ Headers personalizados → No evita el bloqueo
5. ❌ Múltiples player_clients → No evita el bloqueo
6. ❌ Configuración conservadora de yt-dlp → No evita el bloqueo

**Conclusión**: El único factor determinante es la dirección IP de origen. Si es de datacenter, YouTube lo bloquea. No hay workaround conocido que funcione de forma fiable y gratuita.
