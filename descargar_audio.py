import yt_dlp
import os
import sys
import argparse
import csv
from pathlib import Path

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
                    print(f"📝 URL {len(urls)}: {url}")
                elif url:
                    print(f"⚠️  Fila {row_num}: URL inválida '{url}' (ignorada)")
                    
    except FileNotFoundError:
        print(f"❌ No se pudo encontrar el archivo: {archivo_csv}")
        return []
    except Exception as e:
        print(f"❌ Error leyendo el archivo CSV: {e}")
        return []
    
    print(f"\n📊 Se encontraron {len(urls)} URLs válidas para procesar.\n")
    return urls

def progress_hook(d):
    """Hook para mostrar el progreso de descarga de manera segura"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        print(f"\rDescargando... {percent} a {speed}", end='', flush=True)
    elif d['status'] == 'finished':
        print(f"\n✓ Descarga terminada: {d.get('filename', 'archivo')}")
    elif d['status'] == 'error':
        print(f"\n✗ Error durante la descarga")

def descargar_audio_mp3(url_youtube, output_dir='.'):
    """
    Descarga el audio de un video de YouTube y lo guarda en formato MP3.

    :param url_youtube: La URL del video de YouTube.
    :param output_dir: Directorio donde guardar el archivo (por defecto: directorio actual)
    :return: Ruta del archivo MP3 creado o None si hay error
    """
    
    # ⚙️ Opciones de yt-dlp
    ydl_opts = {
        # 🎵 Formato del post-procesamiento (extraer audio)
        'format': 'bestaudio/best',  
        'postprocessors': [{
            # 🔄 Post-procesador para convertir el archivo
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320', # Calidad de audio (320 kbps es alta)
        }],
        # 📁 Plantilla del nombre de archivo. %(title)s es el título del video.
        # yt-dlp añadirá automáticamente la extensión .mp3
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        # 📢 Mostrar progreso
        'progress_hooks': [progress_hook],
        # ⚠️ Desactivar listas de reproducción si se pega una URL de lista
        'noplaylist': True,
        # 🔇 Silenciar salida de youtube-dl excepto errores
        'quiet': False 
    }

    try:
        print(f"Iniciando descarga de audio para: {url_youtube}")
        
        # Crear directorio de salida si no existe
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # 🚀 Ejecutar la descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Obtener metadatos para verificar el nombre del archivo
            info = ydl.extract_info(url_youtube, download=False)
            title = info.get('title', 'audio')
            # Limpiar caracteres problemáticos del nombre de archivo
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            final_filename = os.path.join(output_dir, f"{safe_title}.mp3")
            
            # Ahora forzamos la descarga real
            ydl.download([url_youtube])

        print(f"\n✅ ¡Descarga completada con éxito!")
        print(f"El archivo MP3 se ha guardado como: '{final_filename}'")
        return final_filename

    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Error de descarga (asegúrate de que la URL es correcta y el video está disponible): {e}")
        return None
    except Exception as e:
        print(f"\n❌ Ha ocurrido un error inesperado. Asegúrate de que FFmpeg está instalado y en el PATH. Error: {e}")
        return None

def main():
    """Función principal con manejo de argumentos mejorado"""
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
        '--version',
        action='version',
        version='YouTube to MP3 Downloader v1.1'
    )
    
    args = parser.parse_args()
    
    urls_a_procesar = []
    
    # Modo CSV: procesar múltiples URLs desde archivo
    if args.csv_file:
        print(f"📁 Procesando URLs desde archivo CSV: {args.csv_file}\n")
        urls_a_procesar = leer_urls_csv(args.csv_file)
        
        if not urls_a_procesar:
            print("❌ No se encontraron URLs válidas en el archivo CSV.")
            return 1
    
    # Modo individual: una sola URL
    else:
        url = args.url
        if not url:
            try:
                url = input("Pega la URL del video de YouTube aquí: ").strip()
            except KeyboardInterrupt:
                print("\n❌ Operación cancelada por el usuario.")
                return 1
        
        if not url:
            print("❌ No se proporcionó ninguna URL.")
            return 1
        
        # Validación básica de URL
        if not (url.startswith('http://') or url.startswith('https://')):
            print("❌ La URL debe comenzar con http:// o https://")
            return 1
            
        urls_a_procesar = [url]
    
    # Procesar todas las URLs
    total_urls = len(urls_a_procesar)
    exitosos = 0
    fallidos = 0
    
    print(f"🚀 Iniciando procesamiento de {total_urls} URL(s)...\n")
    
    for i, url in enumerate(urls_a_procesar, 1):
        print(f"\n{'='*60}")
        print(f"🎧 Procesando {i}/{total_urls}: {url}")
        print(f"{'='*60}")
        
        try:
            resultado = descargar_audio_mp3(url, args.output_dir)
            
            if resultado:
                exitosos += 1
                print(f"✅ {i}/{total_urls} - Éxito: {url}")
            else:
                fallidos += 1
                print(f"❌ {i}/{total_urls} - Fallo: {url}")
                
        except KeyboardInterrupt:
            print(f"\n\n⏸️  Procesamiento interrumpido por el usuario.")
            print(f"📊 Resumen hasta el momento:")
            print(f"   ✅ Exitosos: {exitosos}")
            print(f"   ❌ Fallidos: {fallidos}")
            print(f"   ⏸️  Restantes: {total_urls - i}")
            return 1
        except Exception as e:
            fallidos += 1
            print(f"❌ {i}/{total_urls} - Error inesperado con {url}: {e}")
    
    # Resumen final
    print(f"\n\n{'='*60}")
    print(f"📊 RESUMEN FINAL")
    print(f"{'='*60}")
    print(f"📝 URLs procesadas: {total_urls}")
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    
    if fallidos == 0:
        print(f"\n🎉 ¡Todos los archivos se descargaron exitosamente!")
        return 0
    elif exitosos > 0:
        print(f"\n⚠️  Procesamiento completado con algunos errores.")
        return 0
    else:
        print(f"\n❌ Todos los intentos de descarga fallaron.")
        return 1

# Bloque principal para la ejecución
if __name__ == "__main__":
    sys.exit(main())
