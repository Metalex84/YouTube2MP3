# ================================================================================
# CONFIGURADOR AUTOMÁTICO - YouTube to MP3 Converter
# ================================================================================
# Este script configura automáticamente todo lo necesario para ejecutar el
# YouTube to MP3 Converter en cualquier ordenador Windows.
# ================================================================================

param(
    [switch]$SkipFFmpeg,
    [switch]$Verbose
)

# Configuración
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"

# URLs y versiones
$PYTHON_VERSION = "3.11.9"
$PYTHON_URL = "https://www.python.org/ftp/python/$PYTHON_VERSION/python-$PYTHON_VERSION-amd64.exe"
$FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

# Colores para output
function Write-ColorOutput([string]$Message, [string]$Color = "White") {
    switch($Color) {
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        "Magenta" { Write-Host $Message -ForegroundColor Magenta }
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

# Función para verificar si el script se ejecuta como administrador
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Función para verificar Python
function Test-Python {
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            
            if ($major -ge 3 -and $minor -ge 7) {
                Write-Success "Python encontrado: $pythonVersion"
                return $true
            } else {
                Write-Error "Python encontrado pero versión muy antigua: $pythonVersion (necesario Python 3.7+)"
                return $false
            }
        }
        return $false
    }
    catch {
        Write-Info "Python no está instalado o no está en PATH"
        return $false
    }
}

# Función para instalar Python
function Install-Python {
    Write-Header "INSTALANDO PYTHON"
    
    $tempPath = Join-Path $env:TEMP "python-installer.exe"
    
    try {
        Write-Step "Descargando Python $PYTHON_VERSION..."
        Invoke-WebRequest -Uri $PYTHON_URL -OutFile $tempPath -UseBasicParsing
        
        Write-Step "Instalando Python (esto puede tardar unos minutos)..."
        $installArgs = @(
            "/quiet",
            "InstallAllUsers=1",
            "PrependPath=1",
            "Include_test=0",
            "Include_pip=1"
        )
        
        Start-Process -FilePath $tempPath -ArgumentList $installArgs -Wait
        
        # Actualizar variables de entorno para la sesión actual
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        Write-Success "Python instalado correctamente"
        
        # Verificar instalación
        Start-Sleep 3
        if (Test-Python) {
            return $true
        } else {
            Write-Error "La instalación de Python no se completó correctamente"
            return $false
        }
    }
    catch {
        Write-Error "Error instalando Python: $($_.Exception.Message)"
        return $false
    }
    finally {
        if (Test-Path $tempPath) {
            Remove-Item $tempPath -Force
        }
    }
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
        Write-Info "FFmpeg no está instalado o no está en PATH"
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

# Función para configurar entorno virtual
function Setup-VirtualEnvironment {
    Write-Header "CONFIGURANDO ENTORNO VIRTUAL"
    
    $venvPath = ".\venv"
    
    try {
        # Crear entorno virtual si no existe
        if (-not (Test-Path $venvPath)) {
            Write-Step "Creando entorno virtual..."
            python -m venv $venvPath
            Write-Success "Entorno virtual creado"
        } else {
            Write-Info "Entorno virtual ya existe"
        }
        
        # Activar entorno virtual e instalar dependencias
        Write-Step "Instalando dependencias..."
        
        $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
        & $activateScript
        
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
        Write-Success "Dependencias instaladas correctamente"
        return $true
    }
    catch {
        Write-Error "Error configurando entorno virtual: $($_.Exception.Message)"
        return $false
    }
}

# Función para verificar el proyecto
function Test-Project {
    Write-Header "VERIFICANDO INSTALACIÓN"
    
    try {
        Write-Step "Verificando archivos del proyecto..."
        
        $requiredFiles = @("descargar_audio.py", "requirements.txt")
        foreach ($file in $requiredFiles) {
            if (-not (Test-Path $file)) {
                Write-Error "Archivo requerido no encontrado: $file"
                return $false
            }
        }
        
        Write-Step "Probando script principal..."
        
        $activateScript = ".\venv\Scripts\Activate.ps1"
        $testCommand = "& '$activateScript'; python descargar_audio.py --version"
        
        $result = Invoke-Expression $testCommand
        
        if ($result -match "YouTube to MP3 Downloader") {
            Write-Success "Proyecto configurado correctamente"
            Write-Success "Versión: $result"
            return $true
        } else {
            Write-Error "El script principal no responde correctamente"
            return $false
        }
    }
    catch {
        Write-Error "Error verificando proyecto: $($_.Exception.Message)"
        return $false
    }
}

# Función principal
function Main {
    Write-Header "CONFIGURADOR AUTOMÁTICO - YouTube to MP3 Converter"
    Write-Info "Este script configurará automáticamente todo lo necesario para ejecutar el programa."
    Write-Info "Presiona Ctrl+C en cualquier momento para cancelar."
    Write-Host ""
    
    # Verificar si estamos en el directorio correcto
    if (-not (Test-Path "descargar_audio.py")) {
        Write-Error "Este script debe ejecutarse desde el directorio del proyecto (donde está descargar_audio.py)"
        exit 1
    }
    
    $needsAdmin = $false
    
    # Verificar Python
    if (-not (Test-Python)) {
        Write-Info "Python necesita ser instalado. Esto requiere permisos de administrador."
        $needsAdmin = $true
    }
    
    # Verificar permisos de administrador si es necesario
    if ($needsAdmin -and -not (Test-Administrator)) {
        Write-Error "Se necesitan permisos de administrador para instalar Python."
        Write-Info "Por favor, ejecuta este script como administrador o instala Python manualmente desde:"
        Write-Info "https://www.python.org/downloads/"
        exit 1
    }
    
    # Instalar Python si es necesario
    if (-not (Test-Python)) {
        if (-not (Install-Python)) {
            Write-Error "No se pudo instalar Python. Configuración abortada."
            exit 1
        }
    }
    
    # Verificar/instalar FFmpeg (opcional)
    if (-not $SkipFFmpeg) {
        if (-not (Test-FFmpeg)) {
            if (-not (Install-FFmpeg)) {
                Write-Error "No se pudo instalar FFmpeg. El programa funcionará pero sin conversión a MP3."
                Write-Info "Puedes instalar FFmpeg manualmente más tarde desde: https://ffmpeg.org/"
            }
        }
    } else {
        Write-Info "Omitiendo instalación de FFmpeg (especificado con -SkipFFmpeg)"
    }
    
    # Configurar entorno virtual
    if (-not (Setup-VirtualEnvironment)) {
        Write-Error "No se pudo configurar el entorno virtual. Configuración abortada."
        exit 1
    }
    
    # Verificar instalación
    if (-not (Test-Project)) {
        Write-Error "La verificación final falló. Revisa los errores anteriores."
        exit 1
    }
    
    # Éxito
    Write-Header "¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!"
    Write-Success "El YouTube to MP3 Converter está listo para usar."
    Write-Host ""
    Write-Info "Para ejecutar el programa, usa:"
    Write-ColorOutput "  .\ejecutar.ps1 --help" "Green"
    Write-ColorOutput "  .\ejecutar.ps1 `"https://www.youtube.com/watch?v=VIDEO_ID`"" "Green"
    Write-ColorOutput "  .\ejecutar.ps1 --csv-file urls.csv" "Green"
    Write-Host ""
}

# Ejecutar función principal
try {
    Main
}
catch {
    Write-Error "Error inesperado: $($_.Exception.Message)"
    exit 1
}