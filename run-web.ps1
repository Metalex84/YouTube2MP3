#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Wrapper script to build and run the YouTube2MP3 Web application in Docker.

.DESCRIPTION
    This script builds the Docker image and runs the web application container
    with all necessary dependencies (Flask, SocketIO, FFmpeg).

.PARAMETER Build
    Force rebuild of the Docker image even if it exists.

.PARAMETER Stop
    Stop and remove the running container.

.PARAMETER Logs
    Show logs from the running container.

.PARAMETER Clean
    Remove container and image completely.

.PARAMETER Port
    Port to expose the web application (default: 5000).

.EXAMPLE
    .\run-web.ps1
    Start the web application (builds if needed).

.EXAMPLE
    .\run-web.ps1 -Build
    Force rebuild and start the application.

.EXAMPLE
    .\run-web.ps1 -Stop
    Stop the running container.

.EXAMPLE
    .\run-web.ps1 -Logs
    Show container logs.

.EXAMPLE
    .\run-web.ps1 -Port 8080
    Run on port 8080 instead of 5000.
#>

param(
    [switch]$Build,
    [switch]$Stop,
    [switch]$Logs,
    [switch]$Clean,
    [int]$Port = 5000
)

# Configuration
$IMAGE_NAME = "youtube2mp3-web"
$CONTAINER_NAME = "youtube2mp3-web"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$DOWNLOADS_DIR = Join-Path $SCRIPT_DIR "downloads"
$LOGS_DIR = Join-Path $SCRIPT_DIR "logs"

# Colors for output
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[+] $Message" "Green"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[i] $Message" "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[!] $Message" "Yellow"
}

function Write-Error-Custom {
    param([string]$Message)
    Write-ColorOutput "[x] $Message" "Red"
}

# Check if Docker is installed
function Test-Docker {
    try {
        $null = docker --version 2>&1
        return $true
    } catch {
        return $false
    }
}

# Check if container exists
function Test-ContainerExists {
    $result = docker ps -a --filter "name=^/${CONTAINER_NAME}$" --format "{{.Names}}" 2>$null
    return $result -eq $CONTAINER_NAME
}

# Check if container is running
function Test-ContainerRunning {
    $result = docker ps --filter "name=^/${CONTAINER_NAME}$" --format "{{.Names}}" 2>$null
    return $result -eq $CONTAINER_NAME
}

# Check if image exists
function Test-ImageExists {
    $result = docker images -q $IMAGE_NAME 2>$null
    return ![string]::IsNullOrEmpty($result)
}

# Stop and remove container
function Stop-Container {
    Write-Info "Stopping container..."
    
    if (Test-ContainerRunning) {
        docker stop $CONTAINER_NAME | Out-Null
        Write-Success "Container stopped"
    }
    
    if (Test-ContainerExists) {
        docker rm $CONTAINER_NAME | Out-Null
        Write-Success "Container removed"
    }
}

# Build Docker image
function Build-Image {
    Write-Info "Building Docker image..."
    
    Set-Location $SCRIPT_DIR
    docker build -t $IMAGE_NAME .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Image built successfully"
        return $true
    } else {
        Write-Error-Custom "Failed to build image"
        return $false
    }
}

# Create directories if they don't exist
function Initialize-Directories {
    if (!(Test-Path $DOWNLOADS_DIR)) {
        New-Item -ItemType Directory -Path $DOWNLOADS_DIR -Force | Out-Null
        Write-Info "Created downloads directory"
    }
    
    if (!(Test-Path $LOGS_DIR)) {
        New-Item -ItemType Directory -Path $LOGS_DIR -Force | Out-Null
        Write-Info "Created logs directory"
    }
}

# Run container
function Start-Container {
    Write-Info "Starting container on port ${Port}..."
    
    docker run -d `
        --name $CONTAINER_NAME `
        -p "${Port}:5000" `
        -v "${DOWNLOADS_DIR}:/app/downloads" `
        -v "${LOGS_DIR}:/app/logs" `
        -e PYTHONUNBUFFERED=1 `
        -e PYTHONIOENCODING=utf-8 `
        -e DOWNLOAD_DIR=/app/downloads `
        -e LOGS_DIR=/app/logs `
        --restart unless-stopped `
        $IMAGE_NAME
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container started successfully"
        Write-Info "Web application available at: http://localhost:${Port}"
        return $true
    } else {
        Write-Error-Custom "Failed to start container"
        return $false
    }
}

# Show logs
function Show-Logs {
    Write-Info "Showing container logs (Ctrl+C to exit)..."
    docker logs -f $CONTAINER_NAME
}

# Clean everything
function Remove-Everything {
    Write-Warning "This will remove the container and image completely."
    $confirm = Read-Host "Are you sure? (y/N)"
    
    if ($confirm -ne "y" -and $confirm -ne "Y") {
        Write-Info "Cancelled"
        return
    }
    
    Stop-Container
    
    if (Test-ImageExists) {
        Write-Info "Removing image..."
        docker rmi $IMAGE_NAME | Out-Null
        Write-Success "Image removed"
    }
}

# Main script logic
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  YouTube2MP3 Web Application - Docker" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker installation
if (!(Test-Docker)) {
    Write-Error-Custom "Docker is not installed or not running"
    Write-Info "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Handle different operations
if ($Clean) {
    Remove-Everything
    exit 0
}

if ($Stop) {
    Stop-Container
    exit 0
}

if ($Logs) {
    if (!(Test-ContainerRunning)) {
        Write-Error-Custom "Container is not running"
        exit 1
    }
    Show-Logs
    exit 0
}

# Main flow: Build and Run
Initialize-Directories

# Check if image exists or force rebuild
if ($Build -or !(Test-ImageExists)) {
    if (!(Build-Image)) {
        exit 1
    }
}

# Stop existing container if running
if (Test-ContainerRunning) {
    Write-Info "Container already running, stopping it first..."
    Stop-Container
}

# Remove existing container if exists
if (Test-ContainerExists) {
    docker rm $CONTAINER_NAME | Out-Null
}

# Start the container
if (Start-Container) {
    Write-Host ""
    Write-Success "Application is ready!"
    Write-Host ""
    Write-Info "Access the web interface at: http://localhost:${Port}"
    Write-Info "View logs with: .\run-web.ps1 -Logs"
    Write-Info "Stop with: .\run-web.ps1 -Stop"
    Write-Host ""
} else {
    Write-Error-Custom "Failed to start application"
    exit 1
}
