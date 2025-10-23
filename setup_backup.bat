@echo off
REM ====================================================================
REM Script para configurar backup automático diario en Windows
REM Ejecutar este archivo como Administrador
REM ====================================================================

echo ============================================================
echo CONFIGURANDO BACKUP AUTOMATICO DEL ESTACIONAMIENTO
echo ============================================================
echo.

REM Obtener la ruta del proyecto
set PROJECT_PATH=%~dp0
set PYTHON_PATH=%PROJECT_PATH%venv\Scripts\python.exe
set BACKUP_SCRIPT=%PROJECT_PATH%backup_manager.py

echo Ruta del proyecto: %PROJECT_PATH%
echo Ruta de Python: %PYTHON_PATH%
echo Script de backup: %BACKUP_SCRIPT%
echo.

REM Crear tarea programada para ejecutar a las 23:00 todos los días
echo Creando tarea programada...
schtasks /Create /SC DAILY /TN "Backup_Estacionamiento" /TR "\"%PYTHON_PATH%\" \"%BACKUP_SCRIPT%\"" /ST 23:00 /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo BACKUP AUTOMATICO CONFIGURADO EXITOSAMENTE
    echo ============================================================
    echo.
    echo La tarea se ejecutara todos los dias a las 23:00
    echo.
    echo Para ver la tarea: 
    echo   - Panel de Control ^> Herramientas Administrativas ^> Programador de Tareas
    echo   - Buscar: "Backup_Estacionamiento"
    echo.
    echo Para ejecutar backup manualmente:
    echo   python backup_manager.py
    echo.
) else (
    echo.
    echo ERROR: No se pudo crear la tarea programada
    echo Asegurese de ejecutar este script como Administrador
    echo.
)

pause