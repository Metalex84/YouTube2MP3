// Global state
let socket = null;
let activeDownloads = new Map();

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
}

// API call to start single download
async function startSingleDownload(url) {
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
            addDownloadToUI({
                id: data.download_id,
                url: url,
                status: 'pending',
                title: 'Cargando...'
            });
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Error starting download:', error);
        alert('Error al iniciar la descarga');
    }
}

// API call to upload CSV
async function uploadCSV(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/batch-download', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        
        if (response.ok) {
            alert(`Se iniciaron ${data.count} descargas`);
            // Load downloads will be updated via WebSocket
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        console.error('Error uploading CSV:', error);
        alert('Error al subir el archivo CSV');
    }
}

// API call to start batch download from URLs
async function startBatchDownload(urls) {
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
            alert(`Se iniciaron ${data.count} descargas`);
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
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

    const element = document.getElementById(`download-${data.download_id}`);
    if (element) {
        element.innerHTML = createDownloadHTML(download);
    }
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
}
