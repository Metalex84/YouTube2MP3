# Instrucciones para Probar la Función de Descarga ZIP

## Estado de la Implementación
✅ La función de descarga ZIP ha sido completamente implementada.

## Cómo Probar la Función

### Paso 1: Iniciar el Servidor
```bash
python app.py
```

El servidor debería iniciar en `http://localhost:5000`

### Paso 2: Verificar el Estado Inicial
Abre otra terminal y ejecuta:
```bash
python check_downloads.py
```

Este script te mostrará:
- Cuántas descargas hay en total
- Cuántas están completadas
- Si el botón ZIP debería aparecer (necesita ≥2 completadas)

### Paso 3: Completar Descargas
1. Abre el navegador en `http://localhost:5000`
2. Ve a la pestaña "Descarga en Lote"
3. Opciones:
   - **Opción A**: Sube un archivo CSV con al menos 2 URLs
   - **Opción B**: Pega al menos 2 URLs en el área de texto (una por línea)

Ejemplo de URLs para probar:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=jNQXAC9IVRw
```

### Paso 4: Esperar que se Completen
- Las descargas aparecerán en la sección "Descargas Activas"
- Verás barras de progreso durante la descarga
- Espera a que al menos 2 muestren el estado "✅ Completado"

### Paso 5: Verificar el Botón ZIP
Una vez que 2 o más descargas estén completadas:
- **El botón "📦 Descargar Todas (ZIP)" debería aparecer automáticamente** en el encabezado de "Descargas Activas"
- Si no aparece, abre la consola del navegador (F12) y busca mensajes de debug

### Paso 6: Descargar el ZIP
1. Haz clic en el botón "📦 Descargar Todas (ZIP)"
2. El navegador debería descargar un archivo `.zip` con nombre tipo:
   `youtube2mp3_batch_20251215_221507.zip`
3. Abre el archivo ZIP y verifica que contiene todos los archivos MP3

## Debug en la Consola del Navegador

Si el botón no aparece, abre la consola (F12) y busca estos mensajes:

```javascript
[DEBUG] Completed downloads: X  // X debería ser >= 2
[DEBUG] Showing ZIP download button  // Debería aparecer cuando X >= 2
```

Si ves:
```javascript
[ERROR] Download all ZIP button not found!
```
Significa que hay un problema con el HTML.

## Debug en el Servidor

En la terminal donde corre el servidor, cuando hagas clic en el botón ZIP deberías ver:

```
[DEBUG] ZIP download requested
[DEBUG] Found X completed downloads
[DEBUG] Adding to zip: nombre_archivo1.mp3
[DEBUG] Adding to zip: nombre_archivo2.mp3
[DEBUG] Sending ZIP file: youtube2mp3_batch_YYYYMMDD_HHMMSS.zip
```

## Problemas Comunes

### El botón no aparece
- **Causa**: Menos de 2 descargas completadas
- **Solución**: Completa más descargas

### Error "No completed downloads available"
- **Causa**: Las descargas no tienen el campo `filepath` o están en estado incorrecto
- **Solución**: Revisa los logs del servidor durante la descarga

### El ZIP está vacío
- **Causa**: Los archivos MP3 no existen en el sistema de archivos
- **Solución**: Verifica que FFmpeg está correctamente configurado y las descargas se completan sin errores

### El botón aparece pero no hace nada al hacer clic
- **Causa**: Error en JavaScript
- **Solución**: Abre la consola del navegador (F12) y busca errores en rojo

## Verificación Rápida sin Interfaz

Para probar el endpoint directamente:
```bash
# En el navegador o con curl
curl -O http://localhost:5000/api/batch-download/zip
```

Si hay descargas completadas, descargará el ZIP directamente.
