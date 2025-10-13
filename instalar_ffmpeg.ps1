# ================================================================================
# INSTALADOR DE FFMPEG - YouTube to MP3 Converter
# ================================================================================
# Script para instalar FFmpeg si se omitió en la configuración inicial
# ================================================================================

# Configuración
$ErrorActionPreference = "Stop"
$FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

# Colores para output
function Write-ColorOutput([string]$Message, [string]$Color = "White") {
    switch($Color) {
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        default { Write-Host $Message }
    }
}

function Write-Header([string]$Message) {
    Write-Host ""
    Write-ColorOutput "=================================================================" "Cyan"
    Write-ColorOutput $Message "Cyan"
    Write-ColorOutput "=================================================================" "Cyan"
}

function Write-Step([string]$Message) {
    Write-ColorOutput "🔧 $Message" "Yellow"
}

function Write-Success([string]$Message) {
    Write-ColorOutput "✅ $Message" "Green"
}

function Write-Error([string]$Message) {
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Info([string]$Message) {
    Write-ColorOutput "ℹ️  $Message" "Cyan"
}

# Función para verificar FFmpeg
function Test-FFmpeg {
    try {
        $ffmpegVersion = ffmpeg -version 2>$null
        if ($ffmpegVersion -match "ffmpeg version") {
            Write-Success "FFmpeg encontrado y funcional"
            return $true
        }
        return $false
    }
    catch {
        return $false
    }
}

# Función para instalar FFmpeg
function Install-FFmpeg {
    Write-Header "INSTALANDO FFMPEG"
    
    $ffmpegDir = Join-Path $env:LOCALAPPDATA "ffmpeg"
    $tempZip = Join-Path $env:TEMP "ffmpeg.zip"
    
    try {
        Write-Step "Descargando FFmpeg..."
        Invoke-WebRequest -Uri $FFMPEG_URL -OutFile $tempZip -UseBasicParsing
        
        Write-Step "Extrayendo FFmpeg..."
        if (Test-Path $ffmpegDir) {
            Remove-Item $ffmpegDir -Recurse -Force
        }
        New-Item -ItemType Directory -Path $ffmpegDir -Force | Out-Null
        
        Expand-Archive -Path $tempZip -DestinationPath $ffmpegDir -Force
        
        # Encontrar el directorio bin
        $binPath = Get-ChildItem -Path $ffmpegDir -Recurse -Directory -Name "bin" | Select-Object -First 1
        if ($binPath) {
            $fullBinPath = Join-Path $ffmpegDir $binPath
            
            Write-Step "Añadiendo FFmpeg al PATH del sistema..."
            
            # Obtener PATH actual
            $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
            
            # Verificar si ya está en PATH
            if ($currentPath -notlike "*$fullBinPath*") {
                $newPath = $currentPath + ";" + $fullBinPath
                [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
                
                # Actualizar PATH para la sesión actual
                $env:Path += ";" + $fullBinPath
            }
            
            Write-Success "FFmpeg instalado correctamente"
            
            # Verificar instalación
            Start-Sleep 2
            if (Test-FFmpeg) {
                return $true
            } else {
                Write-Error "La instalación de FFmpeg no se completó correctamente"
                Write-Info "Es posible que necesites abrir una nueva ventana de PowerShell"
                return $false
            }
        } else {
            Write-Error "No se pudo encontrar el directorio bin de FFmpeg"
            return $false
        }
    }
    catch {
        Write-Error "Error instalando FFmpeg: $($_.Exception.Message)"
        return $false
    }
    finally {
        if (Test-Path $tempZip) {
            Remove-Item $tempZip -Force
        }
    }
}

# Función principal
function Main {
    Write-Header "INSTALADOR DE FFMPEG - YouTube to MP3 Converter"
    Write-Info "Este script instalará FFmpeg que es necesario para la conversión a MP3."
    Write-Host ""
    
    # Verificar FFmpeg
    if (Test-FFmpeg) {
        Write-Success "FFmpeg ya está instalado y funcionando correctamente."
        Write-Info "No es necesario hacer nada más."
        return
    }
    
    Write-Info "FFmpeg no está instalado. Procediendo con la instalación..."
    Write-Host ""
    
    # Instalar FFmpeg
    if (Install-FFmpeg) {
        Write-Header "¡FFMPEG INSTALADO EXITOSAMENTE!"
        Write-Success "FFmpeg está ahora disponible para convertir videos a MP3."
        Write-Host ""
        Write-Info "Puedes ejecutar el programa normalmente:"
        Write-ColorOutput "  .\ejecutar.ps1 `"https://www.youtube.com/watch?v=VIDEO_ID`"" "Green"
        Write-Host ""
    } else {
        Write-Header "ERROR EN LA INSTALACIÓN"
        Write-Error "No se pudo instalar FFmpeg automáticamente."
        Write-Host ""
        Write-Info "Opciones alternativas:"
        Write-Info "1. Abre una nueva ventana de PowerShell y prueba de nuevo"
        Write-Info "2. Descarga FFmpeg manualmente desde: https://ffmpeg.org/"
        Write-Info "3. Usa Chocolatey: choco install ffmpeg"
        Write-Info "4. Usa Scoop: scoop install ffmpeg"
        Write-Host ""
        exit 1
    }
}

# Ejecutar función principal
try {
    Main
}
catch {
    Write-Error "Error inesperado: $($_.Exception.Message)"
    exit 1
}