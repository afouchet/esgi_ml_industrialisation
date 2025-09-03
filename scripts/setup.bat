@echo off
echo Installing project...

where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Install uv...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
)

uv sync --dev
echo Install finished !
echo To activate environment: .venv\Scripts\activate
pause
