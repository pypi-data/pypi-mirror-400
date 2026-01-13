@echo off
REM Mind v5 - Quick Start Script for Windows
REM Usage: mind.bat [start|stop|status|logs]

set COMMAND=%1
if "%COMMAND%"=="" set COMMAND=start

cd /d "%~dp0"

if "%COMMAND%"=="start" (
    echo Starting Mind v5...
    docker-compose up -d
    echo.
    echo Waiting for services to initialize...
    timeout /t 10 /nobreak >nul
    echo.
    echo Mind v5 is ready!
    echo   API:          http://localhost:8080
    echo   Health:       http://localhost:8080/health
    echo   Metrics:      http://localhost:8080/metrics
    echo   Temporal UI:  http://localhost:8088
    echo.
    echo To use with Claude Code, add to claude_desktop_config.json:
    echo   "mind": { "command": "uvx", "args": ["--from", "mind-mcp", "mind-mcp"] }
    goto :eof
)

if "%COMMAND%"=="stop" (
    echo Stopping Mind v5...
    docker-compose down
    echo Mind stopped.
    goto :eof
)

if "%COMMAND%"=="status" (
    docker-compose ps
    goto :eof
)

if "%COMMAND%"=="logs" (
    docker-compose logs -f --tail=50
    goto :eof
)

if "%COMMAND%"=="test" (
    echo Running E2E test...
    curl -s http://localhost:8080/health
    echo.
    goto :eof
)

echo Usage: mind.bat [start^|stop^|status^|logs^|test]
