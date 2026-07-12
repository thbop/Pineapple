@echo off

:: Ensure user has uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo Setting up game launcher...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)


uv run main.py