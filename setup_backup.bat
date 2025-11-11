@echo off
REM ====================================================================
REM Script para configurar 2 backups:
REM   1. Diario (23:00 todos los días)
REM   2. Mensual (23:30 el día 1 de cada mes)
REM Ejecutar este archivo como Administrador
REM ====================================================================

echo ============================================================
echo CONFIGURANDO BACKUPS: DIARIO Y MENSUAL
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

REM ====================================================================
REM ELIMINAR TAREAS ANTIGUAS SI EXISTEN
REM ====================================================================
echo Limpiando tareas antiguas...
schtasks /Delete /TN "Backup_Estacionamiento" /F >nul 2>&1
schtasks /Delete /TN "Backup_Estacionamiento_Mediodia" /F >nul 2>&1
schtasks /Delete /TN "Backup_Estacionamiento_Tarde" /F >nul 2>&1
schtasks /Delete /TN "Backup_Estacionamiento_Nocturno" /F >nul 2>&1
echo    ✓ Tareas antiguas eliminadas
echo.

REM ====================================================================
REM BACKUP DIARIO: Todos los días a las 23:00
REM ====================================================================
echo [1/2] Configurando backup DIARIO (23:00)...
schtasks /Create /SC DAILY /TN "Backup_Diario_Estacionamiento" /TR "\"%PYTHON_PATH%\" \"%BACKUP_SCRIPT%\"" /ST 23:00 /F

if %ERRORLEVEL% EQU 0 (
    echo    ✅ Backup diario configurado correctamente
) else (
    echo    ❌ Error al configurar backup diario
)

echo.

REM ====================================================================
REM BACKUP MENSUAL: Día 1 de cada mes a las 23:30
REM ====================================================================
echo [2/2] Configurando backup MENSUAL (dia 1 a las 23:30)...
schtasks /Create /SC MONTHLY /D 1 /TN "Backup_Mensual_Estacionamiento" /TR "\"%PYTHON_PATH%\" \"%BACKUP_SCRIPT%\"" /ST 23:30 /F

if %ERRORLEVEL% EQU 0 (
    echo    ✅ Backup mensual configurado correctamente
) else (
    echo    ❌ Error al configurar backup mensual
)

echo.
echo ============================================================
echo CONFIGURACION COMPLETADA
echo ============================================================
echo.
echo Se configuraron 2 tareas de backup:
echo.
echo   📅 DIARIO:   Todos los dias a las 23:00
echo              (Backup_Diario_Estacionamiento)
echo.
echo   📆 MENSUAL:  Dia 1 de cada mes a las 23:30
echo              (Backup_Mensual_Estacionamiento)
echo.
echo ============================================================
echo VERIFICACION
echo ============================================================
echo.
echo Para verificar las tareas:
echo   1. Abrir: Programador de Tareas (taskschd.msc)
echo   2. Buscar: "Backup_Diario_Estacionamiento"
echo   3. Buscar: "Backup_Mensual_Estacionamiento"
echo.
echo Para ejecutar backup manual:
echo   python backup_manager.py
echo.
echo ============================================================
echo.

pause