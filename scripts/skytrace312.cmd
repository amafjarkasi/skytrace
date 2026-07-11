@echo off
REM Activate Python 3.12 local-inference environment for SkyTrace
call "%~dp0..\.venv312\Scripts\activate.bat"
cd /d "%~dp0.."
python -m skytrace.cli %*
