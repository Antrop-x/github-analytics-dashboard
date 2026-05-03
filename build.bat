@echo off
REM GitHub Analytics Dashboard - Windows Build Script
REM Commands: build, test, run, clean

if "%1"=="" (
    echo GitHub Analytics Dashboard - Commands
    echo.
    echo Usage: build.bat [command]
    echo.
    echo Commands:
    echo   build          Install dependencies
    echo   test           Run all tests
    echo   test-verbose   Run tests with verbose output
    echo   run            Run the Streamlit app
    echo   clean          Clean up cache and temporary files
    echo.
    goto end
)

if "%1"=="build" (
    echo Installing dependencies...
    pip install -r requirements.txt
    goto end
)

if "%1"=="test" (
    echo Running tests...
    python -m pytest tests/
    goto end
)

if "%1"=="test-verbose" (
    echo Running tests with verbose output...
    python -m pytest tests/ -v -s
    goto end
)

if "%1"=="run" (
    echo Starting Streamlit app...
    streamlit run app.py
    goto end
)

if "%1"=="clean" (
    echo Cleaning up...
    for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
    for /d /r . %%d in (.pytest_cache) do @if exist "%%d" rd /s /q "%%d"
    for /d /r . %%d in (.coverage) do @if exist "%%d" rd /s /q "%%d"
    for /d /r . %%d in (htmlcov) do @if exist "%%d" rd /s /q "%%d"
    del /s /q *.pyc 2>nul
    echo Clean complete!
    goto end
)

echo Unknown command: %1
:end
