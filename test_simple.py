import requests
import time

BASE_URL = "http://localhost:5000"

# Probar descarga por lotes con JSON
print("=" * 60)
print("🧪 PRUEBA DE DESCARGA POR LOTES")
print("=" * 60)

urls = [
    "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
]

print(f"\n📋 Iniciando descarga de {len(urls)} videos...")
response = requests.post(
    f"{BASE_URL}/api/batch-download",
    json={'urls': urls}
)

if response.status_code in [200, 202]:
    data = response.json()
    download_ids = data.get('download_ids', [])
    print(f"✅ Descargas iniciadas: {len(download_ids)}")
    print(f"   IDs: {download_ids}")
    
    print("\n⏳ Monitoreando progreso...")
    
    completed = set()
    failed = set()
    
    for i in range(30):  # Máximo 30 iteraciones (90 segundos)
        print(f"\n--- Iteración {i+1} ---")
        
        for download_id in download_ids:
            if download_id in completed or download_id in failed:
                continue
            
            response = requests.get(f"{BASE_URL}/api/download/{download_id}")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                title = data.get('title', 'N/A')
                
                if status == 'completed':
                    completed.add(download_id)
                    print(f"✅ {title} - COMPLETADO")
                    print(f"   Archivo: {data.get('filename')}")
                elif status == 'failed':
                    failed.add(download_id)
                    print(f"❌ {title} - FALLIDO")
                    print(f"   Error: {data.get('error', 'Unknown')}")
                elif status == 'downloading':
                    print(f"⬇️  {title} - Descargando...")
                elif status == 'pending':
                    print(f"⏳ {title or download_id[:8]} - En cola")
        
        if len(completed) + len(failed) == len(download_ids):
            break
        
        time.sleep(3)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    print(f"   Total: {len(download_ids)}")
    print(f"   Completadas: {len(completed)}")
    print(f"   Fallidas: {len(failed)}")
    print(f"   Pendientes: {len(download_ids) - len(completed) - len(failed)}")
    print("=" * 60)
    
    # Listar archivos descargados
    print("\n📁 Verificando archivos en carpeta downloads/...")
    import os
    downloads_dir = "downloads"
    if os.path.exists(downloads_dir):
        mp3_files = [f for f in os.listdir(downloads_dir) if f.endswith('.mp3')]
        print(f"   Archivos MP3 encontrados: {len(mp3_files)}")
        for f in mp3_files[-5:]:  # Últimos 5
            print(f"   - {f}")
    
else:
    print(f"❌ Error: {response.status_code}")
    print(f"   {response.text}")
