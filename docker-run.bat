@echo off
REM YouTube to MP3 Downloader - Docker Runner Script (Batch)

setlocal EnableDelayedExpansion

REM Color definitions for Windows batch
set "INFO_COLOR=0B"
set "SUCCESS_COLOR=0A"
set "WARNING_COLOR=0E"
set "ERROR_COLOR=0C"
set "RESET_COLOR=07"

REM Utility functions
:print_info
    color %INFO_COLOR%
    echo [INFO] %~1
    color %RESET_COLOR%
    goto :eof

:print_success
    color %SUCCESS_COLOR%
    echo [SUCCESS] %~1
    color %RESET_COLOR%
    goto :eof

:print_warning
    color %WARNING_COLOR%
    echo [WARNING] %~1
    color %RESET_COLOR%
    goto :eof

:print_error
    color %ERROR_COLOR%
    echo [ERROR] %~1
    color %RESET_COLOR%
    goto :eof

REM Show help
:show_help
    echo.
    echo YouTube to MP3 Downloader - Docker Runner
    echo ==========================================
    echo.
    echo Uso: %~nx0 [opcion] [argumentos...]
    echo.
    echo Opciones:
    echo   build                    Construir la imagen Docker
    echo   run [args]               Ejecutar el contenedor con argumentos
    echo   shell                    Abrir shell interactiva en el contenedor
    echo   logs                     Mostrar logs del contenedor
    echo   clean                    Limpiar contenedores e imagenes
    echo   help                     Mostrar esta ayuda
    echo.
    echo Ejemplos:
    echo   %~nx0 build
    echo   %~nx0 run --version
    echo   %~nx0 run "https://youtube.com/watch?v=..."
    echo   %~nx0 run --csv-file urls.csv --max-concurrent 3
    echo.
    goto :eof

REM Create necessary directories
:create_directories
    call :print_info "Creando directorios necesarios..."
    if not exist "downloads" mkdir downloads
    if not exist "logs" mkdir logs
    call :print_success "Directorios creados: .\downloads y .\logs"
    goto :eof

REM Build Docker image
:build_image
    call :print_info "Construyendo imagen Docker..."
    docker build -t youtube-mp3-downloader .
    if %errorlevel% equ 0 (
        call :print_success "Imagen construida exitosamente"
    ) else (
        call :print_error "Error construyendo la imagen"
        exit /b 1
    )
    goto :eof

REM Run container
:run_container
    call :create_directories
    
    call :print_info "Ejecutando contenedor con argumentos: %*"
    
    set "DOCKER_CMD=docker run --rm"
    set "DOCKER_CMD=!DOCKER_CMD! -v "%CD%\downloads:/app/downloads""
    set "DOCKER_CMD=!DOCKER_CMD! -v "%CD%\logs:/app/logs""
    set "DOCKER_CMD=!DOCKER_CMD! -e LOGS_DIR=logs"
    
    REM Add CSV volume if file exists
    if exist "urls.csv" (
        set "DOCKER_CMD=!DOCKER_CMD! -v "%CD%\urls.csv:/app/urls.csv:ro""
    )
    
    set "DOCKER_CMD=!DOCKER_CMD! youtube-mp3-downloader"
    
    REM Check if output directory is specified
    set "HAS_OUTPUT_DIR=false"
    set "TEMP_ARGS=%*"
    echo %TEMP_ARGS% | find "-o" >nul && set "HAS_OUTPUT_DIR=true"
    echo %TEMP_ARGS% | find "--output-dir" >nul && set "HAS_OUTPUT_DIR=true"
    
    REM Add default output directory if not specified
    if "%HAS_OUTPUT_DIR%"=="false" (
        set "DOCKER_CMD=!DOCKER_CMD! -o downloads"
    )
    
    REM Add all remaining arguments
    :add_args_loop
    if "%~1"=="" goto run_docker
    set "DOCKER_CMD=!DOCKER_CMD! "%~1""
    shift
    goto add_args_loop
    
    :run_docker
    !DOCKER_CMD!
    goto :eof

REM Interactive shell
:run_shell
    call :create_directories
    
    call :print_info "Abriendo shell interactiva..."
    docker run --rm -it ^
        -v "%CD%\downloads:/app/downloads" ^
        -v "%CD%\logs:/app/logs" ^
        --entrypoint /bin/bash ^
        youtube-mp3-downloader
    goto :eof

REM Show logs
:show_logs
    if exist "logs\youtube_downloader.log" (
        call :print_info "Mostrando logs recientes..."
        powershell -Command "Get-Content 'logs\youtube_downloader.log' -Tail 50 -Wait"
    ) else (
        call :print_warning "No se encontraron logs"
    )
    goto :eof

REM Clean Docker
:clean_docker
    call :print_warning "Limpiando contenedores e imagenes..."
    docker container prune -f
    docker image rm youtube-mp3-downloader 2>nul
    call :print_success "Limpieza completada"
    goto :eof

REM Check if Docker is installed
:check_docker
    docker --version >nul 2>&1
    if %errorlevel% neq 0 (
        call :print_error "Docker no esta instalado o no esta en el PATH"
        exit /b 1
    )
    goto :eof

REM Main function
:main
    call :check_docker
    
    set "command=%~1"
    if "%command%"=="" set "command=help"
    
    if /i "%command%"=="build" (
        call :build_image
    ) else if /i "%command%"=="run" (
        shift
        call :run_container %*
    ) else if /i "%command%"=="shell" (
        call :run_shell
    ) else if /i "%command%"=="logs" (
        call :show_logs
    ) else if /i "%command%"=="clean" (
        call :clean_docker
    ) else if /i "%command%"=="help" (
        call :show_help
    ) else if /i "%command%"=="--help" (
        call :show_help
    ) else if /i "%command%"=="-h" (
        call :show_help
    ) else (
        call :print_error "Opcion desconocida: %command%"
        call :show_help
        exit /b 1
    )
    goto :eof

REM Execute main function
call :main %*