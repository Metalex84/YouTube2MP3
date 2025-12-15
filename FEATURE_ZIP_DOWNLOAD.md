# Batch ZIP Download Feature

## Overview
The application now supports downloading all completed MP3 files as a single compressed ZIP archive. This feature is particularly useful when processing multiple YouTube URLs via CSV upload or batch text input.

## How It Works

### User Interface
- When **2 or more downloads are completed**, a "📦 Descargar Todas (ZIP)" button automatically appears in the Downloads section header
- Clicking this button downloads all completed MP3 files in a single ZIP archive
- The ZIP file is named with a timestamp: `youtube2mp3_batch_YYYYMMDD_HHMMSS.zip`

### Backend API
- **Endpoint**: `GET /api/batch-download/zip`
- **Response**: ZIP file containing all completed MP3 downloads
- **Error Handling**: Returns 404 if no completed downloads are available

## Technical Implementation

### Backend (`app.py`)
- New endpoint `/api/batch-download/zip` creates a temporary ZIP file
- Iterates through all completed downloads and adds their MP3 files to the archive
- Uses `zipfile` module with `ZIP_DEFLATED` compression
- Automatically cleans up temporary files after sending

### Frontend (`script.js`)
- `updateDownloadAllButton()`: Shows/hides the ZIP download button based on completed downloads count
- `downloadAllAsZip()`: Fetches the ZIP file and triggers browser download
- Button visibility is updated when:
  - Downloads complete
  - Downloads fail
  - Existing downloads are loaded on page load

### UI (`index.html`)
- Button added to Downloads section header with flexbox layout
- Initially hidden (display: none) until conditions are met

## Testing

Run the test script to verify functionality:
```bash
python test_zip_download.py
```

The test script will:
1. Check for completed downloads
2. Request the ZIP file from the API
3. Verify the ZIP file is valid
4. List the contents of the archive

## Requirements
- At least 2 completed downloads for the button to appear
- All completed downloads with valid file paths are included in the ZIP
- Python's `zipfile` module (included in standard library)

## Future Enhancements
Possible improvements:
- Add option to select specific files to include in the ZIP
- Show ZIP file size before download
- Add progress indicator for large batches
- Allow custom ZIP filename
