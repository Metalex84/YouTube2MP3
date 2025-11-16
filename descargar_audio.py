import yt_dlp
import os
import sys
import argparse
import csv
from pathlib import Path
import asyncio
import concurrent.futures
from threading import Lock, Thread, Event
import time
import logging
from datetime import datetime

# Fix Windows console encoding issues
def setup_console_encoding():
    """Configure console for Unicode output on Windows"""
    if sys.platform.startswith('win'):
        try:
            # For Python 3.7+ on Windows, just set the encoding environment variable
            # and let Python handle the console encoding automatically
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            # Try to reconfigure stdout and stderr to use utf-8 with error handling
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, OSError, TypeError, UnicodeError):
            # If that fails, we'll use emoji fallbacks
            pass

# Emoji fallbacks for Windows console
def safe_print(*args, **kwargs):
    """Print function that handles Unicode characters safely"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Replace problematic Unicode characters with ASCII alternatives
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                # Replace common emojis with text equivalents
                safe_arg = arg.replace('📁', '[FOLDER]')
                safe_arg = safe_arg.replace('📝', '[NOTE]')
                safe_arg = safe_arg.replace('⚠️', '[WARNING]')
                safe_arg = safe_arg.replace('❌', '[ERROR]')
                safe_arg = safe_arg.replace('📊', '[STATS]')
                safe_arg = safe_arg.replace('✓', '[OK]')
                safe_arg = safe_arg.replace('✗', '[FAIL]')
                safe_arg = safe_arg.replace('✅', '[SUCCESS]')
                safe_arg = safe_arg.replace('🚀', '[START]')
                safe_arg = safe_arg.replace('🎧', '[AUDIO]')
                safe_arg = safe_arg.replace('🎉', '[CELEBRATE]')
                safe_arg = safe_arg.replace('⏸️', '[PAUSE]')
                safe_arg = safe_arg.replace('🔄', '[PROCESS]')
                safe_arg = safe_arg.replace('🎵', '[MUSIC]')
                safe_arg = safe_arg.replace('📢', '[INFO]')
                safe_arg = safe_arg.replace('🔇', '[QUIET]')
                safe_arg = safe_arg.replace('⚙️', '[SETTINGS]')
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)

# Initialize console encoding
setup_console_encoding()

# Configure logging
def setup_logging():
    """Configure logging to file with timestamp"""
    # Skip if logging is already configured
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return None
    
    logs_dir = os.environ.get('LOGS_DIR', '.')
    
    # Create logs directory if it doesn't exist
    Path(logs_dir).mkdir(parents=True, exist_ok=True)
    
    log_filename = os.path.join(logs_dir, 'youtube_downloader.log')
    
    # Configure logging (mode='a' to append instead of truncate)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, mode='a', encoding='utf-8'),
        ]
    )
    
    # Log session start
    logging.info("="*50)
    logging.info("Nueva sesion de YouTube to MP3 Downloader iniciada")
    logging.info("="*50)
    
    return log_filename

# Initialize logging only when module is run directly (not imported)
log_file = None

# Always ensure basic logging is configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Thread-safe printing lock
print_lock = Lock()

def thread_safe_print(*args, **kwargs):
    """Thread-safe version of safe_print"""
    with print_lock:
        safe_print(*args, **kwargs)

def log_warning(message):
    """Log warning messages to file instead of printing"""
    logging.warning(message)

def log_info(message):
    """Log info messages to file"""
    logging.info(message)

def log_error(message):
    """Log error messages to file and print to console"""
    logging.error(message)
    thread_safe_print(f"[ERROR] {message}")

class ProgressAnimation:
    """Animated progress indicator for console"""
    
    def __init__(self, message="Procesando"):
        self.message = message
        self.is_running = False
        self.thread = None
        self.stop_event = Event()
        self.frames = ['|', '/', '-', '\\']
        self.current_frame = 0
        
    def _animate(self):
        """Run the animation in a separate thread"""
        while not self.stop_event.is_set():
            with print_lock:
                frame = self.frames[self.current_frame]
                print(f"\r{frame} {self.message}...", end='', flush=True)
                self.current_frame = (self.current_frame + 1) % len(self.frames)
            time.sleep(0.2)
    
    def start(self):
        """Start the animation"""
        if not self.is_running:
            self.is_running = True
            self.stop_event.clear()
            self.thread = Thread(target=self._animate, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the animation"""
        if self.is_running:
            self.stop_event.set()
            self.is_running = False
            if self.thread:
                self.thread.join(timeout=1)
            with print_lock:
                print("\r" + " " * (len(self.message) + 10) + "\r", end='', flush=True)
    
    def update_message(self, new_message):
        """Update the animation message"""
        self.message = new_message

def leer_urls_csv(archivo_csv):
    """
    Lee URLs desde un archivo CSV.
    
    :param archivo_csv: Ruta al archivo CSV
    :return: Lista de URLs válidas
    """
    urls = []
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8', newline='') as file:
            # Leer todo el contenido y analizar
            content = file.read().strip()
            file.seek(0)
            
            # Detectar si es probable que tenga encabezados
            lines = content.split('\n')
            has_header = False
            
            if lines and len(lines) > 1:
                first_line = lines[0].strip()
                # Si la primera línea parece ser un encabezado (no una URL)
                if not (first_line.startswith('http://') or first_line.startswith('https://')):
                    has_header = True
            
            reader = csv.reader(file)
            
            if has_header:
                next(reader)  # Saltar encabezado
            
            for row_num, row in enumerate(reader, start=1):
                if not row:  # Saltar filas vacías
                    continue
                    
                # Tomar la primera columna como URL
                url = row[0].strip() if row[0] else None
                
                if url and (url.startswith('http://') or url.startswith('https://')):
                    urls.append(url)
                    safe_print(f"[NOTE] URL {len(urls)}: {url}")
                    log_info(f"URL {len(urls)} agregada: {url}")
                elif url:
                    log_warning(f"Fila {row_num}: URL invalida '{url}' (ignorada)")
                    
    except FileNotFoundError:
        safe_print(f"[ERROR] No se pudo encontrar el archivo: {archivo_csv}")
        return []
    except Exception as e:
        safe_print(f"[ERROR] Error leyendo el archivo CSV: {e}")
        return []
    
    safe_print(f"\n[STATS] Se encontraron {len(urls)} URLs validas para procesar.\n")
    return urls

def progress_hook(url_id, animation=None):
    """Factory function to create thread-specific progress hooks"""
    def hook(d):
        """Hook para mostrar el progreso de descarga de manera segura y thread-safe"""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            log_info(f"[{url_id}] Descargando... {percent} a {speed}")
            if animation:
                animation.update_message(f"[{url_id}] Descargando {percent}")
        elif d['status'] == 'finished':
            log_info(f"[{url_id}] Descarga terminada: {d.get('filename', 'archivo')}")
            if animation:
                animation.update_message(f"[{url_id}] Convirtiendo a MP3")
        elif d['status'] == 'error':
            log_error(f"[{url_id}] Error durante la descarga")
    return hook

def descargar_audio_mp3(url_youtube, output_dir='.', url_id=None, show_animation=True):
    """
    Descarga el audio de un video de YouTube y lo guarda en formato MP3.

    :param url_youtube: La URL del video de YouTube.
    :param output_dir: Directorio donde guardar el archivo (por defecto: directorio actual)
    :param url_id: Identificador para el hilo de descarga (para logging thread-safe)
    :param show_animation: Mostrar animacion de progreso
    :return: Ruta del archivo MP3 creado o None si hay error
    """
    
    # Generar ID si no se proporciona
    if url_id is None:
        url_id = f"URL-{hash(url_youtube) % 1000:03d}"
    
    # Crear animacion de progreso
    animation = None
    if show_animation:
        animation = ProgressAnimation(f"[{url_id}] Iniciando descarga")
        animation.start()
    
    # Log inicio de descarga
    log_info(f"[{url_id}] Iniciando descarga de: {url_youtube}")
    
    # [SETTINGS] Opciones de yt-dlp
    ydl_opts = {
        # [MUSIC] Formato del post-procesamiento (extraer audio)
        'format': 'bestaudio/best',  
        'postprocessors': [{
            # [PROCESS] Post-procesador para convertir el archivo
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320', # Calidad de audio (320 kbps es alta)
        }],
        # [FOLDER] Plantilla del nombre de archivo. %(title)s es el titulo del video.
        # yt-dlp aniadira automaticamente la extension .mp3
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        # [INFO] Mostrar progreso
        'progress_hooks': [progress_hook(url_id, animation)],
        # [WARNING] Desactivar listas de reproduccion si se pega una URL de lista
        'noplaylist': True,
        # [QUIET] Silenciar salida de youtube-dl excepto errores
        'quiet': True  # Silenciar para que solo se vea nuestra animacion
    }

    try:
        # Crear directorio de salida si no existe
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        if animation:
            animation.update_message(f"[{url_id}] Obteniendo informacion del video")
        
        # [START] Ejecutar la descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Obtener metadatos para verificar el nombre del archivo
            info = ydl.extract_info(url_youtube, download=False)
            title = info.get('title', 'audio')
            log_info(f"[{url_id}] Titulo del video: {title}")
            
            # Limpiar caracteres problematicos del nombre de archivo
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            final_filename = os.path.join(output_dir, f"{safe_title}.mp3")
            
            if animation:
                animation.update_message(f"[{url_id}] Descargando audio")
            
            # Ahora forzamos la descarga real
            ydl.download([url_youtube])

        # Detener animacion y mostrar exito
        if animation:
            animation.stop()
        
        thread_safe_print(f"[SUCCESS] [{url_id}] '{title}' -> MP3 completado")
        log_info(f"[{url_id}] Descarga completada exitosamente: {final_filename}")
        return final_filename

    except yt_dlp.utils.DownloadError as e:
        if animation:
            animation.stop()
        error_msg = f"Error de descarga para {url_youtube}: {str(e)}"
        log_error(f"[{url_id}] {error_msg}")
        return None
    except Exception as e:
        if animation:
            animation.stop()
        error_msg = f"Error inesperado procesando {url_youtube}: {str(e)}"
        log_error(f"[{url_id}] {error_msg}")
        return None

async def procesar_url_async(url, output_dir, url_id, executor):
    """
    Procesa una URL de forma asincrona usando un ThreadPoolExecutor.
    
    :param url: URL del video de YouTube
    :param output_dir: Directorio de salida
    :param url_id: Identificador unico para el hilo
    :param executor: ThreadPoolExecutor instance
    :return: Tuple (url, resultado, exito)
    """
    loop = asyncio.get_event_loop()
    
    try:
        # Ejecutar la descarga en un hilo separado con animacion
        resultado = await loop.run_in_executor(
            executor, 
            descargar_audio_mp3, 
            url, 
            output_dir, 
            url_id,
            True  # show_animation
        )
        
        exito = resultado is not None
        return (url, resultado, exito, url_id)
        
    except Exception as e:
        error_msg = f"Error procesando {url}: {str(e)}"
        log_error(f"[{url_id}] {error_msg}")
        return (url, None, False, url_id)

async def procesar_urls_async(urls, output_dir, max_concurrent=3):
    """
    Procesa multiples URLs de forma asincrona con un limite de concurrencia.
    
    :param urls: Lista de URLs a procesar
    :param output_dir: Directorio de salida
    :param max_concurrent: Numero maximo de descargas simultaneas (default: 3)
    :return: Tuple (exitosos, fallidos, resultados)
    """
    total_urls = len(urls)
    exitosos = 0
    fallidos = 0
    resultados = []
    
    thread_safe_print(f"[START] Procesamiento asincrono: {total_urls} URL(s), max {max_concurrent} hilos")
    log_info(f"Iniciando procesamiento asincrono de {total_urls} URLs con hasta {max_concurrent} hilos simultaneos")
    
    # Crear un ThreadPoolExecutor con el numero maximo de hilos
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        
        # Crear tareas asincronas para cada URL
        tasks = []
        for i, url in enumerate(urls, 1):
            url_id = f"T{i:02d}"
            log_info(f"Creando tarea {url_id} para: {url}")
            task = procesar_url_async(url, output_dir, url_id, executor)
            tasks.append(task)
        
        thread_safe_print(f"[PROCESS] Ejecutando {len(tasks)} tareas en paralelo...")
        
        try:
            # Ejecutar todas las tareas de forma concurrente
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Procesar resultados
            for i, result in enumerate(completed_tasks, 1):
                if isinstance(result, Exception):
                    fallidos += 1
                    error_msg = f"Tarea {i} fallo con excepcion: {result}"
                    log_error(error_msg)
                    resultados.append((urls[i-1], None, False, f"T{i:02d}"))
                else:
                    url, archivo, exito, url_id = result
                    if exito:
                        exitosos += 1
                        # Solo mostrar el resultado final, los detalles van al log
                        log_info(f"{url_id} - Exito: {url}")
                    else:
                        fallidos += 1
                        # Los errores ya se loggearon en la funcion individual
                        pass
                    resultados.append(result)
            
        except KeyboardInterrupt:
            thread_safe_print(f"\n[PAUSE] Procesamiento interrumpido por el usuario.")
            log_info("Procesamiento interrumpido por el usuario")
            # Cancelar tareas pendientes
            for task in tasks:
                if not task.done():
                    task.cancel()
            raise
    
    return exitosos, fallidos, resultados

def main():
    """Función principal con manejo de argumentos mejorado"""
    # Initialize logging for CLI usage
    global log_file
    log_file = setup_logging()
    
    parser = argparse.ArgumentParser(
        description='Descarga audio de YouTube y lo convierte a MP3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python descargar_audio.py "https://www.youtube.com/watch?v=VIDEO_ID"
  python descargar_audio.py -o /ruta/destino "https://www.youtube.com/watch?v=VIDEO_ID"
  python descargar_audio.py --csv-file urls.csv
  python descargar_audio.py --csv-file urls.csv -o /ruta/destino
  python descargar_audio.py  # Te pedirá la URL interactivamente
        """
    )
    
    parser.add_argument(
        'url', 
        nargs='?', 
        help='URL del video de YouTube (ignorado si se usa --csv-file)'
    )
    parser.add_argument(
        '-o', '--output-dir',
        default='.',
        help='Directorio donde guardar el archivo MP3 (por defecto: directorio actual)'
    )
    parser.add_argument(
        '--csv-file',
        help='Archivo CSV con URLs a procesar (una URL por fila)'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=3,
        help='Numero maximo de descargas simultaneas (por defecto: 3)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='YouTube to MP3 Downloader v1.2 (Async)'
    )
    
    args = parser.parse_args()
    
    urls_a_procesar = []
    
    # Mostrar informacion del archivo de log
    thread_safe_print(f"[INFO] Log de la sesion: {log_file}")
    
    # Validar max_concurrent
    if args.max_concurrent < 1:
        safe_print("[ERROR] El numero maximo de descargas concurrentes debe ser al menos 1.")
        return 1
    elif args.max_concurrent > 10:
        log_warning("Se recomienda no usar mas de 10 descargas simultaneas para evitar problemas.")
    
    # Modo CSV: procesar multiples URLs desde archivo
    if args.csv_file:
        safe_print(f"[FOLDER] Procesando URLs desde archivo CSV: {args.csv_file}\n")
        urls_a_procesar = leer_urls_csv(args.csv_file)
        
        if not urls_a_procesar:
            safe_print("[ERROR] No se encontraron URLs validas en el archivo CSV.")
            return 1
    
    # Modo individual: una sola URL
    else:
        url = args.url
        if not url:
            try:
                url = input("Pega la URL del video de YouTube aqui: ").strip()
            except KeyboardInterrupt:
                safe_print("\n[ERROR] Operacion cancelada por el usuario.")
                return 1
        
        if not url:
            safe_print("[ERROR] No se proporciono ninguna URL.")
            return 1
        
        # Validacion basica de URL
        if not (url.startswith('http://') or url.startswith('https://')):
            safe_print("[ERROR] La URL debe comenzar con http:// o https://")
            return 1
            
        urls_a_procesar = [url]
    
    # Procesar todas las URLs de forma asincrona
    total_urls = len(urls_a_procesar)
    
    # Decide si usar procesamiento asincrono o sincronico
    usar_async = total_urls > 1 and args.max_concurrent > 1
    
    if usar_async:
        thread_safe_print(f"[INFO] Modo asincrono con hasta {args.max_concurrent} hilos")
        try:
            # Ejecutar el procesamiento asincrono
            exitosos, fallidos, resultados = asyncio.run(
                procesar_urls_async(urls_a_procesar, args.output_dir, args.max_concurrent)
            )
        except KeyboardInterrupt:
            safe_print(f"\n[PAUSE] Procesamiento interrumpido por el usuario.")
            return 1
        except Exception as e:
            error_msg = f"Error durante el procesamiento asincrono: {e}"
            log_error(error_msg)
            return 1
    else:
        # Procesamiento sincronico para URL unica o max_concurrent = 1
        thread_safe_print(f"[INFO] Modo sincronico")
        exitosos = 0
        fallidos = 0
        
        for i, url in enumerate(urls_a_procesar, 1):
            safe_print(f"\n{'='*60}")
            safe_print(f"[AUDIO] Procesando {i}/{total_urls}: {url}")
            safe_print(f"{'='*60}")
            
            try:
                url_id = f"S{i:02d}"
                resultado = descargar_audio_mp3(url, args.output_dir, url_id)
                
                if resultado:
                    exitosos += 1
                    safe_print(f"[SUCCESS] {i}/{total_urls} - Exito: {url}")
                else:
                    fallidos += 1
                    safe_print(f"[FAIL] {i}/{total_urls} - Fallo: {url}")
                    
            except KeyboardInterrupt:
                safe_print(f"\n\n[PAUSE] Procesamiento interrumpido por el usuario.")
                safe_print(f"[STATS] Resumen hasta el momento:")
                safe_print(f"   [SUCCESS] Exitosos: {exitosos}")
                safe_print(f"   [FAIL] Fallidos: {fallidos}")
                safe_print(f"   [PAUSE] Restantes: {total_urls - i}")
                return 1
            except Exception as e:
                fallidos += 1
                safe_print(f"[ERROR] {i}/{total_urls} - Error inesperado con {url}: {e}")
    
    # Resumen final
    safe_print(f"\n\n{'='*60}")
    safe_print(f"[STATS] RESUMEN FINAL")
    safe_print(f"{'='*60}")
    safe_print(f"[NOTE] URLs procesadas: {total_urls}")
    safe_print(f"[SUCCESS] Exitosos: {exitosos}")
    safe_print(f"[FAIL] Fallidos: {fallidos}")
    safe_print(f"[INFO] Log detallado: {log_file}")
    
    # Log del resumen final
    log_info(f"Resumen final - URLs: {total_urls}, Exitosos: {exitosos}, Fallidos: {fallidos}")
    
    if fallidos == 0:
        safe_print(f"\n[CELEBRATE] Todos los archivos se descargaron exitosamente!")
        log_info("Sesion completada exitosamente - todos los archivos descargados")
        return 0
    elif exitosos > 0:
        safe_print(f"\n[WARNING] Procesamiento completado con algunos errores.")
        log_warning("Sesion completada con algunos errores")
        return 0
    else:
        safe_print(f"\n[ERROR] Todos los intentos de descarga fallaron.")
        log_error("Sesion fallida - todos los intentos fallaron")
        return 1

# Bloque principal para la ejecución
if __name__ == "__main__":
    try:
        exit_code = main()
        log_info(f"Programa terminado con codigo de salida: {exit_code}")
        log_info("="*50)
        sys.exit(exit_code)
    except Exception as e:
        log_error(f"Error fatal en el programa principal: {e}")
        log_info("="*50)
        sys.exit(1)
