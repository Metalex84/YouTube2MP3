# ================================================================================
# EJECUTOR - YouTube to MP3 Converter
# ================================================================================
# Script simplificado para ejecutar el YouTube to MP3 Converter
# ================================================================================

param(
    [Parameter(Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

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

function Write-Error-Custom([string]$Message) {
    Write-ColorOutput "❌ $Message" "Red"
}

function Write-Info([string]$Message) {
    Write-ColorOutput "ℹ️  $Message" "Cyan"
}

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "descargar_audio.py")) {
    Write-Error-Custom "Este script debe ejecutarse desde el directorio del proyecto."
    Write-Info "Asegúrate de estar en la carpeta donde está descargar_audio.py"
    exit 1
}

# Verificar que existe el entorno virtual
$venvPath = ".\venv"
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $activateScript)) {
    Write-Error-Custom "No se encontró el entorno virtual."
    Write-Info "Ejecuta primero: .\configurar.ps1"
    exit 1
}

# Verificar que Python está disponible
try {
    $pythonVersion = python --version 2>$null
    if (-not $pythonVersion) {
        throw "Python no encontrado"
    }
}
catch {
    Write-Error-Custom "Python no está instalado o no está en PATH."
    Write-Info "Ejecuta primero: .\configurar.ps1"
    exit 1
}

# Función para mostrar ayuda personalizada
function Show-Help {
    Write-Host ""
    Write-ColorOutput "YouTube to MP3 Converter - Ejecutor Simplificado" "Cyan"
    Write-ColorOutput "=================================================" "Cyan"
    Write-Host ""
    Write-ColorOutput "USO:" "Yellow"
    Write-Host "  .\ejecutar.ps1 [opciones] [URL]"
    Write-Host ""
    Write-ColorOutput "EJEMPLOS:" "Yellow"
    Write-Host "  .\ejecutar.ps1 --help                              # Muestra ayuda detallada"
    Write-Host "  .\ejecutar.ps1 --version                           # Muestra versión"
    Write-Host "  .\ejecutar.ps1 `"https://youtube.com/watch?v=...`"   # Descarga una URL"
    Write-Host "  .\ejecutar.ps1 --csv-file urls.csv                 # Procesa archivo CSV"
    Write-Host "  .\ejecutar.ps1 -o `"C:\Musica`" `"https://...`"        # Especifica directorio"
    Write-Host "  .\ejecutar.ps1                                     # Modo interactivo"
    Write-Host ""
    Write-ColorOutput "NOTAS:" "Yellow"
    Write-Host "  • Si no especificas una URL, el programa te pedirá una"
    Write-Host "  • Los archivos MP3 se guardan en el directorio actual por defecto"
    Write-Host "  • Usa Ctrl+C para cancelar en cualquier momento"
    Write-Host ""
}

# Verificar si se pide ayuda local
if ($Arguments.Count -eq 1 -and ($Arguments[0] -eq "-?" -or $Arguments[0] -eq "/?" -or $Arguments[0] -eq "help")) {
    Show-Help
    exit 0
}

try {
    Write-Info "Activando entorno virtual y ejecutando programa..."
    
    # Cambiar al directorio del script para asegurar rutas relativas
    Push-Location $PSScriptRoot
    
    try {
        # Ejecutar usando cmd para mayor compatibilidad
        $cmdArgs = @()
        $cmdArgs += '/c'
        $cmdArgs += $activateScript + ' &&'
        $cmdArgs += 'python'
        $cmdArgs += 'descargar_audio.py'
        
        if ($Arguments.Count -gt 0) {
            $cmdArgs += $Arguments
        }
        
        Write-ColorOutput "🚀 Ejecutando programa..." "Green"
        Write-Host ""
        
        # Usar Start-Process para mejor control
        $process = Start-Process -FilePath "cmd.exe" -ArgumentList $cmdArgs -NoNewWindow -PassThru -Wait
        $exitCode = $process.ExitCode
        
        Write-Host ""
        if ($exitCode -eq 0) {
            Write-ColorOutput "✅ Ejecución completada exitosamente." "Green"
        } else {
            Write-ColorOutput "⚠️  El programa terminó con código de salida: $exitCode" "Yellow"
        }
        
        exit $exitCode
    }
    finally {
        Pop-Location
    }
}
catch {
    Write-Error-Custom "Error ejecutando el programa: $($_.Exception.Message)"
    Write-Info "Si el problema persiste, verifica la configuración ejecutando: .\configurar.ps1"
    exit 1
}