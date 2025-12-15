# Quick Start - Automatic ZIP Download

## What This Does

When you upload a CSV file or paste multiple YouTube URLs, the application will:

1. ✅ Download and convert each video to MP3 individually
2. ✅ Show progress for each download in "Descargas Activas"
3. ✅ **Automatically create a ZIP file** when all downloads complete
4. ✅ **Automatically download the ZIP** to your browser
5. ✅ Show a confirmation card with option to re-download

## How to Use

### Step 1: Start the Server
```bash
python app.py
```

### Step 2: Open Browser
Navigate to: http://localhost:5000

### Step 3: Go to "Descarga en Lote" Tab
Click the "📋 Descarga en Lote" button at the top

### Step 4: Add Your URLs

**Option A - Upload CSV:**
1. Click "📁 Seleccionar archivo CSV"
2. Select your CSV file with YouTube URLs
3. Click "🚀 Subir y Procesar"

**Option B - Paste URLs:**
1. Scroll to the text area
2. Paste your URLs (one per line)
3. Click "🚀 Procesar URLs"

### Step 5: Watch the Loading Animation
- **Beautiful loading overlay appears** with spinning animation
- Real-time statistics show:
  - Completados (completed files)
  - Pendientes (pending files)
  - Total (total files)
- Numbers update as each download completes
- Overlay automatically disappears when done

### Step 6: Monitor Individual Progress
- Behind the overlay, individual downloads appear in "Descargas Activas"
- Each shows progress: ⏳ Pendiente → ⬇️ Descargando → ✅ Completado

### Step 7: ZIP Downloads Automatically!
- When the last file completes, the ZIP is created
- Loading overlay disappears with final stats
- **Your browser automatically downloads the ZIP**
- Look for the file in your Downloads folder
- A green card appears confirming the download

### Step 8: Re-download if Needed
If you need the ZIP again:
1. Look at the green card at the top of "Descargas Activas"
2. Click "🔄 Descargar Nuevamente"

## CSV File Format

Create a CSV file with one column named `url`:

```csv
url
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

## What You'll See

### During Downloads:
```
📊 Descargas Activas

[Individual download cards showing progress bars]
```

### After All Complete:
```
📊 Descargas Activas

┌─────────────────────────────────────────┐
│ 📦 Descarga en Lote Completada  ✅ Descargado │
│ 3 archivo(s) MP3 comprimido(s)          │
│ ✓ Descarga iniciada automáticamente     │
│ [🔄 Descargar Nuevamente]               │
└─────────────────────────────────────────┘

[Individual download cards still visible]
```

## ZIP File Contents

The ZIP file contains:
- All successfully converted MP3 files
- Named with video titles
- Compressed for faster download
- Filename: `youtube2mp3_batch_YYYYMMDD_HHMMSS.zip`

## Troubleshooting

### ZIP doesn't download automatically
- Check browser popup blocker settings
- Look in Downloads folder - it may have downloaded silently
- Click "🔄 Descargar Nuevamente" from the green card

### Some downloads failed
- ZIP still creates with successful files only
- Failed downloads show ❌ Error status
- Check logs for specific error messages

### Can't find the ZIP file
- Check your browser's Downloads folder
- Windows: Usually `C:\Users\YourName\Downloads\`
- Look for filename starting with `youtube2mp3_batch_`

### Need individual files instead
- All individual MP3s remain available
- Click "📥 Descargar MP3" on each download card
- You get both individual files AND the ZIP

## Advanced

### Check Download Status Programmatically
```bash
python check_downloads.py
```

### View Server Logs
Watch the terminal where you ran `python app.py` for detailed logs:
```
[DEBUG] Batch abc123: All downloads complete, creating ZIP...
[DEBUG] Adding to batch ZIP: video1.mp3
[DEBUG] Adding to batch ZIP: video2.mp3
[DEBUG] Batch abc123: ZIP created successfully
```

### API Endpoint
The ZIP is available at:
```
GET /api/batch/{batch_id}/zip
```

## Tips

💡 **Large batches**: Be patient - creating the ZIP for many files takes time

💡 **Multiple batches**: Each batch gets its own ZIP - you can run multiple batches simultaneously

💡 **Keep the page open**: Don't close the browser until the ZIP downloads

💡 **FFmpeg required**: Make sure FFmpeg is installed for MP3 conversion
