@echo off
chcp 65001 > nul
setlocal EnableDelayedExpansion

REM ================================================================================
REM EJECUTOR - YouTube to MP3 Converter
REM ================================================================================
REM Script simple para ejecutar el YouTube to MP3 Converter
REM ================================================================================

echo 🚀 Activando entorno virtual y ejecutando programa...
echo.

REM Verificar que estamos en el directorio correcto
if not exist "descargar_audio.py" (
    echo ❌ Este script debe ejecutarse desde el directorio del proyecto.
    echo ℹ️  Asegúrate de estar en la carpeta donde está descargar_audio.py
    pause
    exit /b 1
)

REM Verificar que existe el entorno virtual
if not exist "venv\Scripts\activate.bat" (
    echo ❌ No se encontró el entorno virtual.
    echo ℹ️  Ejecuta primero: .\configurar.ps1
    pause
    exit /b 1
)

REM Activar entorno virtual y ejecutar
call venv\Scripts\activate.bat
python descargar_audio.py %*

REM Capturar código de salida
set exitcode=!ERRORLEVEL!

echo.
if !exitcode! EQU 0 (
    echo ✅ Ejecución completada exitosamente.
) else (
    echo ⚠️  El programa terminó con código de salida: !exitcode!
)

REM Pausar solo si no es ejecución silenciosa
if "%1" NEQ "--no-pause" pause

exit /b !exitcode!