@echo off
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    start "" .venv\Scripts\python.exe -m zipper9_ui.app
) else (
    start "" python -m zipper9_ui.app
)
