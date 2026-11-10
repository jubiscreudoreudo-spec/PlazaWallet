@echo off
rem Batch - Start.bat - Plaza Wallet - Windows - Python 3.10+
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 plaza_wallet.py
) else (
    python plaza_wallet.py
)
if errorlevel 1 (
    echo.
    echo Could not start. Requires Python 3.10+ with Tkinter.
    echo Falha ao iniciar. Requer Python 3.10+ com Tkinter.
    echo Error al iniciar. Requiere Python 3.10+ con Tkinter.
    pause
)
