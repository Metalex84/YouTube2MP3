# YouTube to MP3 Downloader - Docker Runner Script (PowerShell)

# Funciones de utilidad para colores
function Write-Info([string]$Message) {
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success([string]$Message) {
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning-Custom([string]$Message) {
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom([string]$Message) {
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Función de ayuda
function Show-Help {
    Write-Host ""
    Write-Host "YouTube to MP3 Downloader - Docker Runner" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Uso: .\docker-run.ps1 [opción] [argumentos...]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Opciones:" -ForegroundColor Yellow
    Write-Host "  build                    Construir la imagen Docker"
    Write-Host "  run [args]               Ejecutar el contenedor con argumentos"
    Write-Host "  shell                    Abrir shell interactiva en el contenedor"
    Write-Host "  logs                     Mostrar logs del contenedor"
    Write-Host "  clean                    Limpiar contenedores e imágenes"
    Write-Host "  help                     Mostrar esta ayuda"
    Write-Host ""
    Write-Host "Ejemplos:" -ForegroundColor Yellow
    Write-Host "  .\docker-run.ps1 build"
    Write-Host "  .\docker-run.ps1 run --version"
    Write-Host '  .\docker-run.ps1 run "https://youtube.com/watch?v=..."'
    Write-Host "  .\docker-run.ps1 run --csv-file urls.csv --max-concurrent 3"
    Write-Host ""
}

# Crear directorios necesarios
function Create-Directories {
    Write-Info "Creando directorios necesarios..."
    New-Item -ItemType Directory -Force -Path "downloads" | Out-Null
    New-Item -ItemType Directory -Force -Path "logs" | Out-Null
    Write-Success "Directorios creados: .\downloads y .\logs"
}

# Construir imagen
function Build-Image {
    Write-Info "Construyendo imagen Docker..."
    $result = docker build -t youtube-mp3-downloader .
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Imagen construida exitosamente"
    } else {
        Write-Error-Custom "Error construyendo la imagen"
        exit 1
    }
}

# Ejecutar contenedor
function Run-Container {
    param([string[]]$ContainerArgs)
    
    Create-Directories
    
    Write-Info "Ejecutando contenedor con argumentos: $($ContainerArgs -join ' ')"
    
    $dockerArgs = @(
        "run", "--rm"
        "-v", "$(Get-Location)\downloads:/app/downloads"
        "-v", "$(Get-Location)\logs:/app/logs"
        "-e", "LOGS_DIR=logs"
    )
    
    # Agregar volumen para CSV si existe
    if (Test-Path "urls.csv") {
        $dockerArgs += "-v", "$(Get-Location)\urls.csv:/app/urls.csv:ro"
    }
    
    $dockerArgs += "youtube-mp3-downloader"
    
    # Add default output directory if not specified
    $hasOutputDir = $false
    foreach ($arg in $ContainerArgs) {
        if ($arg -eq "-o" -or $arg -eq "--output-dir") {
            $hasOutputDir = $true
            break
        }
    }
    
    if (-not $hasOutputDir) {
        $dockerArgs += "-o", "downloads"
    }
    
    $dockerArgs += $ContainerArgs
    
    & docker $dockerArgs
}

# Shell interactiva
function Run-Shell {
    Create-Directories
    
    Write-Info "Abriendo shell interactiva..."
    docker run --rm -it `
        -v "$(Get-Location)\downloads:/app/downloads" `
        -v "$(Get-Location)\logs:/app/logs" `
        --entrypoint /bin/bash `
        youtube-mp3-downloader
}

# Mostrar logs
function Show-Logs {
    if (Test-Path "logs\youtube_downloader.log") {
        Write-Info "Mostrando logs recientes..."
        Get-Content "logs\youtube_downloader.log" -Tail 50 -Wait
    } else {
        Write-Warning-Custom "No se encontraron logs"
    }
}

# Limpiar contenedores e imágenes
function Clean-Docker {
    Write-Warning-Custom "Limpiando contenedores e imágenes..."
    docker container prune -f
    docker image rm youtube-mp3-downloader 2>$null
    Write-Success "Limpieza completada"
}

# Verificar que Docker está instalado
function Test-Docker {
    try {
        $null = docker --version
        return $true
    } catch {
        Write-Error-Custom "Docker no está instalado o no está en el PATH"
        return $false
    }
}

# Función principal
function Main {
    if (-not (Test-Docker)) {
        exit 1
    }
    
    $Command = if ($args.Length -gt 0) { $args[0] } else { "help" }
    $Arguments = if ($args.Length -gt 1) { 
        if ($args.Length -eq 2) { @($args[1]) } 
        else { $args[1..($args.Length-1)] }
    } else { @() }
    
    switch ($Command.ToLower()) {
        "build" {
            Build-Image
        }
        "run" {
            Run-Container -ContainerArgs $Arguments
        }
        "shell" {
            Run-Shell
        }
        "logs" {
            Show-Logs
        }
        "clean" {
            Clean-Docker
        }
        default {
            Show-Help
        }
    }
}

# Ejecutar función principal
Main @args
