import yt_dlp
import os
import sys

def descargar_audio_mp3(url_youtube):
    """
    Descarga el audio de un video de YouTube y lo guarda en formato MP3.

    :param url_youtube: La URL del video de YouTube.
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
        'outtmpl': '%(title)s.%(ext)s', 
        # 📢 Mostrar progreso
        'progress_hooks': [lambda d: print(f"Estado: {d['status'].capitalize()} - {d.get('_percent_str', '')}")],
        # ⚠️ Desactivar listas de reproducción si se pega una URL de lista
        'noplaylist': True,
        # 🔇 Silenciar salida de youtube-dl excepto errores
        'quiet': False 
    }

    try:
        print(f"Iniciando descarga de audio para: {url_youtube}")
        
        # 🚀 Ejecutar la descarga
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Obtener metadatos para verificar el nombre del archivo
            info = ydl.extract_info(url_youtube, download=False)
            filename = ydl.prepare_filename(info)
            # El archivo final se llamará (por ejemplo) "Título del Video.mp3"
            final_filename = os.path.splitext(filename)[0] + '.mp3'
            
            # Ahora forzamos la descarga real
            ydl.download([url_youtube])

        print("\n✅ ¡Descarga completada con éxito!")
        print(f"El archivo MP3 se ha guardado como: '{final_filename}'")

    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Error de descarga (asegúrate de que la URL es correcta y el video está disponible): {e}")
    except Exception as e:
        print(f"\n❌ Ha ocurrido un error inesperado. Asegúrate de que FFmpeg está instalado y en el PATH. Error: {e}")

# Bloque principal para la ejecución
if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Si se pasa la URL como argumento de línea de comandos
        url = sys.argv[1]
    else:
        # Si no se pasa, se pide al usuario
        url = input("Pega la URL del video de YouTube aquí: ")

    if url:
        descargar_audio_mp3(url)
    else:
        print("No se proporcionó ninguna URL.")