"""
Script de prueba para probar la funcionalidad de descarga por lotes
"""
import requests
import time
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000"

def test_health():
    """Verificar que el servidor está corriendo"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor está corriendo")
            print(f"   Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ Servidor respondió con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. Asegúrate de que está corriendo.")
        return False
    except Exception as e:
        print(f"❌ Error al verificar el servidor: {e}")
        return False

def test_batch_download_csv():
    """Probar descarga por lotes usando archivo CSV"""
    print("\n📋 Probando descarga por lotes con CSV...")
    
    csv_file = Path("test_urls.csv")
    if not csv_file.exists():
        print(f"❌ Archivo {csv_file} no encontrado")
        return False
    
    try:
        with open(csv_file, 'rb') as f:
            files = {'file': ('test_urls.csv', f, 'text/csv')}
            response = requests.post(
                f"{BASE_URL}/api/batch-download",
                files=files,
                timeout=10
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Descarga por lotes iniciada")
            print(f"   IDs de descarga: {data.get('download_ids', [])}")
            print(f"   Cantidad: {data.get('count', 0)}")
            return data.get('download_ids', [])
        else:
            print(f"❌ Error al iniciar descarga por lotes: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error en descarga por lotes: {e}")
        return []

def test_batch_download_json():
    """Probar descarga por lotes usando JSON"""
    print("\n📋 Probando descarga por lotes con JSON...")
    
    urls = [
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/batch-download",
            json={'urls': urls},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Descarga por lotes iniciada")
            print(f"   IDs de descarga: {data.get('download_ids', [])}")
            print(f"   Cantidad: {data.get('count', 0)}")
            return data.get('download_ids', [])
        else:
            print(f"❌ Error al iniciar descarga por lotes: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error en descarga por lotes: {e}")
        return []

def monitor_downloads(download_ids, max_wait=300):
    """Monitorear el progreso de las descargas"""
    print(f"\n👀 Monitoreando {len(download_ids)} descargas...")
    print("   (Presiona Ctrl+C para detener el monitoreo)\n")
    
    start_time = time.time()
    completed = set()
    failed = set()
    
    try:
        while len(completed) + len(failed) < len(download_ids):
            if time.time() - start_time > max_wait:
                print(f"\n⏰ Tiempo máximo de espera alcanzado ({max_wait}s)")
                break
            
            for download_id in download_ids:
                if download_id in completed or download_id in failed:
                    continue
                
                try:
                    response = requests.get(
                        f"{BASE_URL}/api/download/{download_id}",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        status = data.get('status', 'unknown')
                        title = data.get('title', 'N/A')
                        
                        if status == 'completed':
                            completed.add(download_id)
                            print(f"✅ Completado: {title}")
                            print(f"   Archivo: {data.get('filename', 'N/A')}")
                        elif status == 'failed':
                            failed.add(download_id)
                            print(f"❌ Fallido: {title}")
                            print(f"   Error: {data.get('error', 'Unknown error')}")
                        elif status == 'downloading':
                            print(f"⬇️  Descargando: {title}")
                        elif status == 'pending':
                            print(f"⏳ En cola: {title or download_id}")
                
                except Exception as e:
                    print(f"⚠️  Error al consultar {download_id}: {e}")
            
            time.sleep(3)  # Esperar 3 segundos antes de la siguiente verificación
        
        print("\n" + "="*60)
        print("📊 RESUMEN:")
        print(f"   Total: {len(download_ids)}")
        print(f"   Completadas: {len(completed)}")
        print(f"   Fallidas: {len(failed)}")
        print(f"   Pendientes: {len(download_ids) - len(completed) - len(failed)}")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Monitoreo interrumpido por el usuario")
        print(f"   Completadas hasta ahora: {len(completed)}")
        print(f"   Fallidas hasta ahora: {len(failed)}")

def list_all_downloads():
    """Listar todas las descargas"""
    print("\n📋 Listando todas las descargas...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/downloads", timeout=5)
        if response.status_code == 200:
            data = response.json()
            downloads = data.get('downloads', [])
            print(f"   Total de descargas: {len(downloads)}")
            
            for dl in downloads[-5:]:  # Mostrar las últimas 5
                print(f"\n   ID: {dl.get('id', 'N/A')[:8]}...")
                print(f"   Título: {dl.get('title', 'N/A')}")
                print(f"   Estado: {dl.get('status', 'N/A')}")
                print(f"   Archivo: {dl.get('filename', 'N/A')}")
            
            return True
        else:
            print(f"❌ Error al listar descargas: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error al listar descargas: {e}")
        return False

def main():
    print("="*60)
    print("🧪 PRUEBA DE DESCARGA POR LOTES - YouTube2MP3")
    print("="*60)
    
    # Verificar que el servidor está corriendo
    if not test_health():
        print("\n💡 Inicia el servidor con: python app.py")
        sys.exit(1)
    
    # Elegir método de prueba
    print("\n¿Qué método quieres probar?")
    print("1. Descarga por lotes con CSV")
    print("2. Descarga por lotes con JSON")
    print("3. Ambos")
    
    choice = input("\nSelecciona (1/2/3) [3]: ").strip() or "3"
    
    download_ids = []
    
    if choice in ["1", "3"]:
        ids = test_batch_download_csv()
        download_ids.extend(ids)
    
    if choice in ["2", "3"]:
        ids = test_batch_download_json()
        download_ids.extend(ids)
    
    if not download_ids:
        print("\n❌ No se iniciaron descargas")
        sys.exit(1)
    
    # Monitorear descargas
    monitor_downloads(download_ids)
    
    # Listar todas las descargas
    list_all_downloads()
    
    print("\n✅ Prueba completada")

if __name__ == "__main__":
    main()
