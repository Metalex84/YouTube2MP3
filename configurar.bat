@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

REM ================================================================================
REM CONFIGURADOR AUTOMÁTICO - YouTube to MP3 Converter (Versión Batch)
REM ================================================================================
REM Este script configura automáticamente el entorno virtual y dependencias
REM ================================================================================

echo ================================================================
echo CONFIGURADOR AUTOMÁTICO - YouTube to MP3 Converter
echo ================================================================
echo Este script configurará el entorno virtual y las dependencias.
echo.

REM Verificar que estamos en el directorio correcto
if not exist "descargar_audio.py" (
    echo ❌ Este script debe ejecutarse desde el directorio del proyecto.
    echo ℹ️  Asegúrate de estar en la carpeta donde está descargar_audio.py
    pause
    exit /b 1
)

echo 🔍 Verificando Python...
python --version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Python no está instalado o no está en PATH.
    echo ℹ️  Instala Python desde: https://www.python.org/downloads/
    echo ℹ️  Asegúrate de marcar "Add Python to PATH" durante la instalación.
    pause
    exit /b 1
)

echo ✅ Python encontrado:
python --version

echo.
echo 🔍 Verificando FFmpeg...
ffmpeg -version >nul 2>&1
if !ERRORLEVEL! NEQ 0 (
    echo ⚠️  FFmpeg no está instalado o no está en PATH.
    echo ℹ️  Instala FFmpeg desde: https://ffmpeg.org/download.html
    echo ℹ️  El programa funcionará pero NO convertirá a MP3 sin FFmpeg.
    echo ℹ️  ¿Continuar de todos modos? (S/N)
    
    set /p "continue=>"
    if /i "!continue!" NEQ "S" if /i "!continue!" NEQ "SI" (
        echo Configuración cancelada.
        pause
        exit /b 1
    )
) else (
    echo ✅ FFmpeg encontrado y funcional.
)

echo.
echo ================================================================
echo CONFIGURANDO ENTORNO VIRTUAL
echo ================================================================

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 🔧 Creando entorno virtual...
    python -m venv venv
    if !ERRORLEVEL! NEQ 0 (
        echo ❌ Error creando entorno virtual.
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado.
) else (
    echo ℹ️  Entorno virtual ya existe.
)

echo 🔧 Activando entorno virtual e instalando dependencias...
call venv\Scripts\activate.bat
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Error activando entorno virtual.
    pause
    exit /b 1
)

echo 🔧 Actualizando pip...
python -m pip install --upgrade pip
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Error actualizando pip.
    pause
    exit /b 1
)

echo 🔧 Instalando dependencias desde requirements.txt...
pip install -r requirements.txt
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Error instalando dependencias.
    pause
    exit /b 1
)

echo ✅ Dependencias instaladas correctamente.

echo.
echo ================================================================
echo VERIFICANDO INSTALACIÓN
echo ================================================================

echo 🔧 Probando script principal...
python descargar_audio.py --version
if !ERRORLEVEL! NEQ 0 (
    echo ❌ El script principal no responde correctamente.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!
echo ================================================================
echo ✅ El YouTube to MP3 Converter está listo para usar.
echo.
echo Para ejecutar el programa, usa:
echo   ejecutar.bat "https://www.youtube.com/watch?v=VIDEO_ID"
echo   ejecutar.bat --csv-file urls.csv
echo   ejecutar.bat --help
echo.

pause