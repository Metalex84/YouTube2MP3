// Global state
let socket = null;
let activeDownloads = new Map();
let activeBatches = new Map();
let pendingDownloadsCount = 0;

// Loading overlay functions
function showLoading(message = 'Iniciando descarga') {
    const overlay = document.getElementById('loading-overlay');
    const submessage = document.getElementById('loading-submessage');
    if (overlay) {
        submessage.textContent = message;
        overlay.classList.remove('hidden');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}

function updateLoadingMessage(message) {
    const submessage = document.getElementById('loading-submessage');
    if (submessage) {
        submessage.textContent = message;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeWebSocket();
    setupEventListeners();
    loadExistingDownloads();
});

// Tab switching
function switchTab(tabName) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Add active class to selected tab
    event.target.classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

// WebSocket initialization
function initializeWebSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
    });

    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
    });

    socket.on('connected', (data) => {
        console.log('Server message:', data.message);
    });

    socket.on('download_progress', (data) => {
        updateDownloadProgress(data);
    });

    socket.on('download_complete', (data) => {
        markDownloadComplete(data);
    });

    socket.on('download_error', (data) => {
        markDownloadFailed(data);
    });

    socket.on('batch_complete', (data) => {
        handleBatchComplete(data);
    });
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (connected) {
        statusElement.textContent = '✅ Conectado';
        statusElement.className = 'status-connected';
    } else {
        statusElement.textContent = '⚠️ Desconectado';
        statusElement.className = 'status-disconnected';
    }
}

// Setup event listeners for forms
function setupEventListeners() {
    // Single URL form
    document.getElementById('single-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = document.getElementById('single-url').value.trim();
        if (url) {
            await startSingleDownload(url);
            document.getElementById('single-url').value = '';
        }
    });

    // CSV upload form
    document.getElementById('csv-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('csv-file');
        if (fileInput.files.length > 0) {
            await uploadCSV(fileInput.files[0]);
            fileInput.value = '';
            document.getElementById('file-name').textContent = '';
        }
    });

    // URLs textarea form
    document.getElementById('urls-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const textarea = document.getElementById('urls-textarea');
        const urls = textarea.value
            .split('\n')
            .map(url => url.trim())
            .filter(url => url.startsWith('http'));
        
        if (urls.length > 0) {
            await startBatchDownload(urls);
            textarea.value = '';
        }
    });

    // File input change listener
    document.getElementById('csv-file').addEventListener('change', (e) => {
        const fileName = e.target.files[0]?.name || '';
        document.getElementById('file-name').textContent = fileName;
    });

    // Download all as ZIP button
    document.getElementById('download-all-zip').addEventListener('click', async () => {
        await downloadAllAsZip();
    });
}

// API call to start single download
async function startSingleDownload(url) {
    showLoading('Conectando con YouTube...');
    pendingDownloadsCount = 1;
    
    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        
        if (response.ok) {
            updateLoadingMessage('Descargando y convirtiendo a MP3...');
            addDownloadToUI({
                id: data.download_id,
                url: url,
                status: 'pending',
                title: 'Cargando...'
            });
        } else {
            hideLoading();
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        hideLoading();
        console.error('Error starting download:', error);
        alert('Error al iniciar la descarga');
    }
}

// API call to upload CSV
async function uploadCSV(file) {
    showLoading('Procesando archivo CSV...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/batch-download', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (response.ok) {
            pendingDownloadsCount = data.download_ids.length;
            updateLoadingMessage(`Descargando ${pendingDownloadsCount} archivo(s)...`);
            
            // Track the batch
            if (data.batch_id) {
                activeBatches.set(data.batch_id, {
                    id: data.batch_id,
                    status: 'processing',
                    download_ids: data.download_ids
                });
            }
            // Load downloads will be updated via WebSocket
        } else {
            hideLoading();
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        hideLoading();
        console.error('Error uploading CSV:', error);
        alert('Error al subir el archivo CSV');
    }
}

// API call to start batch download from URLs
async function startBatchDownload(urls) {
    showLoading(`Preparando ${urls.length} descarga(s)...`);
    
    try {
        const response = await fetch('/api/batch-download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ urls })
        });

        const data = await response.json();
        
        if (response.ok) {
            pendingDownloadsCount = data.download_ids.length;
            updateLoadingMessage(`Descargando ${pendingDownloadsCount} archivo(s)...`);
            
            // Track the batch
            if (data.batch_id) {
                activeBatches.set(data.batch_id, {
                    id: data.batch_id,
                    status: 'processing',
                    download_ids: data.download_ids
                });
            }
        } else {
            hideLoading();
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        hideLoading();
        console.error('Error starting batch download:', error);
        alert('Error al iniciar las descargas');
    }
}

// Load existing downloads from server
async function loadExistingDownloads() {
    try {
        const response = await fetch('/api/downloads');
        const data = await response.json();
        
        if (data.downloads && data.downloads.length > 0) {
            data.downloads.forEach(download => {
                addDownloadToUI(download);
            });
        }
        
        // Load batches
        if (data.batches && data.batches.length > 0) {
            data.batches.forEach(batch => {
                activeBatches.set(batch.id, batch);
                if (batch.status === 'completed') {
                    addBatchZipToUI(batch);
                }
            });
        }
        
        updateDownloadAllButton();
    } catch (error) {
        console.error('Error loading downloads:', error);
    }
}

// Add download item to UI
function addDownloadToUI(download) {
    // Check if already exists
    if (activeDownloads.has(download.id)) {
        return;
    }

    activeDownloads.set(download.id, download);

    const container = document.getElementById('downloads-container');
    
    // Remove "no downloads" message if present
    const noDownloads = container.querySelector('.no-downloads');
    if (noDownloads) {
        noDownloads.remove();
    }

    // Create download item element
    const item = document.createElement('div');
    item.className = 'download-item';
    item.id = `download-${download.id}`;
    item.innerHTML = createDownloadHTML(download);

    container.appendChild(item);
}

// Create HTML for download item
function createDownloadHTML(download) {
    const statusClass = `status-${download.status}`;
    const statusText = getStatusText(download.status);
    
    let progressHTML = '';
    if (download.status === 'downloading') {
        progressHTML = `
            <div class="progress-bar">
                <div class="progress-fill" style="width: 0%"></div>
            </div>
            <div class="download-info">
                <span class="download-speed">Velocidad: Calculando...</span>
                <span class="download-eta">Tiempo restante: Calculando...</span>
            </div>
        `;
    }

    let actionsHTML = '';
    if (download.status === 'completed') {
        actionsHTML = `
            <div class="download-actions">
                <a href="/api/download/${download.id}/file" class="btn-download" download>
                    📥 Descargar MP3
                </a>
            </div>
        `;
    }

    return `
        <div class="download-header">
            <div class="download-title">${download.title || 'Cargando...'}</div>
            <div class="download-status ${statusClass}">${statusText}</div>
        </div>
        <div class="download-url">${download.url}</div>
        ${progressHTML}
        ${actionsHTML}
    `;
}

// Get status text in Spanish
function getStatusText(status) {
    const statusMap = {
        'pending': '⏳ Pendiente',
        'downloading': '⬇️ Descargando',
        'completed': '✅ Completado',
        'failed': '❌ Error'
    };
    return statusMap[status] || status;
}

// Update download progress
function updateDownloadProgress(data) {
    const download = activeDownloads.get(data.download_id);
    if (!download) return;

    download.status = data.status;

    const element = document.getElementById(`download-${data.download_id}`);
    if (!element) return;

    // Update status badge
    const statusBadge = element.querySelector('.download-status');
    statusBadge.textContent = getStatusText(data.status);
    statusBadge.className = `download-status status-${data.status}`;

    // Update progress bar and info
    if (data.status === 'downloading' && data.percent) {
        let progressBar = element.querySelector('.progress-fill');
        if (!progressBar) {
            // Create progress elements if they don't exist
            const progressHTML = `
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
                <div class="download-info">
                    <span class="download-speed">Velocidad: Calculando...</span>
                    <span class="download-eta">Tiempo restante: Calculando...</span>
                </div>
            `;
            element.querySelector('.download-url').insertAdjacentHTML('afterend', progressHTML);
            progressBar = element.querySelector('.progress-fill');
        }

        // Update progress
        const percentValue = parseFloat(data.percent.replace('%', ''));
        progressBar.style.width = data.percent;

        // Update speed and ETA
        const speedElement = element.querySelector('.download-speed');
        const etaElement = element.querySelector('.download-eta');
        if (speedElement) speedElement.textContent = `Velocidad: ${data.speed || 'N/A'}`;
        if (etaElement) etaElement.textContent = `Tiempo restante: ${data.eta || 'N/A'}`;
    }
}

// Mark download as complete
function markDownloadComplete(data) {
    const download = activeDownloads.get(data.download_id);
    if (!download) return;

    download.status = 'completed';
    download.title = data.title;
    download.filename = data.filename;
    download.id = data.download_id; // Ensure id is set

    const element = document.getElementById(`download-${data.download_id}`);
    if (element) {
        element.innerHTML = createDownloadHTML(download);
    }
    
    // Hide loading overlay when download completes (for single downloads)
    pendingDownloadsCount--;
    if (pendingDownloadsCount <= 0) {
        hideLoading();
        pendingDownloadsCount = 0;
    } else {
        updateLoadingMessage(`Procesando... ${pendingDownloadsCount} restante(s)`);
    }
    
    updateDownloadAllButton();
}

// Mark download as failed
function markDownloadFailed(data) {
    const download = activeDownloads.get(data.download_id);
    if (!download) return;

    download.status = 'failed';
    download.error = data.error;

    const element = document.getElementById(`download-${data.download_id}`);
    if (element) {
        const statusBadge = element.querySelector('.download-status');
        statusBadge.textContent = getStatusText('failed');
        statusBadge.className = 'download-status status-failed';

        // Add error message
        const errorHTML = `<div class="download-error" style="color: #ef4444; margin-top: 10px;">Error: ${data.error}</div>`;
        element.querySelector('.download-url').insertAdjacentHTML('afterend', errorHTML);
    }
    
    // Hide loading overlay when download fails
    pendingDownloadsCount--;
    if (pendingDownloadsCount <= 0) {
        hideLoading();
        pendingDownloadsCount = 0;
    } else {
        updateLoadingMessage(`Procesando... ${pendingDownloadsCount} restante(s)`);
    }
    
    updateDownloadAllButton();
}

// Download all completed files as ZIP
async function downloadAllAsZip() {
    console.log('[DEBUG] Requesting ZIP download...');
    try {
        const response = await fetch('/api/batch-download/zip');
        console.log(`[DEBUG] Response status: ${response.status}`);
        console.log(`[DEBUG] Response OK: ${response.ok}`);
        
        if (response.ok) {
            // Create a blob from the response
            const blob = await response.blob();
            
            // Get filename from Content-Disposition header or use default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'youtube2mp3_batch.zip';
            if (contentDisposition) {
                const matches = /filename="(.+)"/.exec(contentDisposition);
                if (matches && matches[1]) {
                    filename = matches[1];
                }
            }
            
            // Create a download link and trigger it
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const data = await response.json();
            alert(`Error: ${data.error || 'Failed to download ZIP'}`);
        }
    } catch (error) {
        console.error('Error downloading ZIP:', error);
        alert('Error al descargar el archivo ZIP');
    }
}

// Handle batch completion
function handleBatchComplete(data) {
    console.log('[DEBUG] Batch completed:', data);
    
    // Hide loading overlay
    hideLoading();
    pendingDownloadsCount = 0;
    
    const batch = {
        id: data.batch_id,
        status: 'completed',
        zip_filename: data.zip_filename,
        total_files: data.total_files,
        failed_files: data.failed_files
    };
    
    activeBatches.set(data.batch_id, batch);
    addBatchZipToUI(batch);
    
    // Automatically trigger download
    console.log('[DEBUG] Triggering automatic ZIP download...');
    downloadBatchZip(data.batch_id, data.zip_filename);
}

// Download batch ZIP file automatically
function downloadBatchZip(batchId, filename) {
    const url = `/api/batch/${batchId}/zip`;
    
    // Show notification
    console.log(`[DEBUG] ZIP download triggered: ${filename}`);
    
    // Create a temporary link and trigger download
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
    }, 100);
}

// Add batch ZIP to UI
function addBatchZipToUI(batch) {
    // Check if already exists
    if (document.getElementById(`batch-${batch.id}`)) {
        return;
    }
    
    const container = document.getElementById('downloads-container');
    
    // Remove "no downloads" message if present
    const noDownloads = container.querySelector('.no-downloads');
    if (noDownloads) {
        noDownloads.remove();
    }
    
    // Create batch item element
    const item = document.createElement('div');
    item.className = 'download-item batch-item';
    item.id = `batch-${batch.id}`;
    item.style.borderLeft = '4px solid #10b981';
    
    item.innerHTML = `
        <div class="download-header">
            <div class="download-title">📦 Descarga en Lote Completada</div>
            <div class="download-status status-completed">✅ Descargado</div>
        </div>
        <div class="download-url">
            ${batch.total_files} archivo(s) MP3 comprimido(s)<br>
            <small style="color: #10b981;">✓ Descarga iniciada automáticamente</small>
        </div>
        <div class="download-actions" style="margin-top: 15px;">
            <a href="/api/batch/${batch.id}/zip" class="btn-download" download onclick="event.preventDefault(); downloadBatchZip('${batch.id}', '${batch.zip_filename}'); return false;">
                🔄 Descargar Nuevamente
            </a>
        </div>
    `;
    
    // Insert at the top of the container
    container.insertBefore(item, container.firstChild);
}

// Update visibility of "Download All as ZIP" button
function updateDownloadAllButton() {
    const completedCount = Array.from(activeDownloads.values())
        .filter(d => d.status === 'completed').length;
    
    console.log(`[DEBUG] Completed downloads: ${completedCount}`);
    
    const button = document.getElementById('download-all-zip');
    if (!button) {
        console.error('[ERROR] Download all ZIP button not found!');
        return;
    }
    
    if (completedCount >= 2) {
        console.log('[DEBUG] Showing ZIP download button');
        button.style.display = 'block';
    } else {
        console.log('[DEBUG] Hiding ZIP download button');
        button.style.display = 'none';
    }
}
