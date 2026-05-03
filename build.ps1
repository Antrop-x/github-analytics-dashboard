# GitHub Analytics Dashboard - PowerShell Build Script
# Usage: .\build.ps1 -Command test

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("build", "test", "test-verbose", "test-coverage", "run", "clean", "help")]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "GitHub Analytics Dashboard - Build Commands" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\build.ps1 -Command [command]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build           Install dependencies"
    Write-Host "  test            Run all tests"
    Write-Host "  test-verbose    Run tests with verbose output"
    Write-Host "  test-coverage   Run tests with coverage report"
    Write-Host "  run             Run the Streamlit app"
    Write-Host "  clean           Clean up cache and temporary files"
    Write-Host "  help            Show this help message"
}

function Invoke-Build {
    Write-Host "Installing dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
}

function Invoke-Test {
    Write-Host "Running tests..." -ForegroundColor Green
    python -m pytest tests/
}

function Invoke-TestVerbose {
    Write-Host "Running tests with verbose output..." -ForegroundColor Green
    python -m pytest tests/ -v -s
}

function Invoke-TestCoverage {
    Write-Host "Running tests with coverage report..." -ForegroundColor Green
    python -m pytest tests/ --cov=. --cov-report=html --cov-report=term
}

function Invoke-Run {
    Write-Host "Starting Streamlit app..." -ForegroundColor Green
    streamlit run app.py
}

function Invoke-Clean {
    Write-Host "Cleaning up..." -ForegroundColor Green
    
    Get-ChildItem -Path . -Include __pycache__ -Recurse -Force -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Get-ChildItem -Path . -Include .pytest_cache -Recurse -Force -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Get-ChildItem -Path . -Include .coverage -Recurse -Force -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Get-ChildItem -Path . -Include htmlcov -Recurse -Force -ErrorAction SilentlyContinue | 
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Get-ChildItem -Path . -Filter *.pyc -Recurse -Force -ErrorAction SilentlyContinue | 
        Remove-Item -Force -ErrorAction SilentlyContinue
    
    Write-Host "Clean complete!" -ForegroundColor Green
}

switch ($Command) {
    "build" { Invoke-Build }
    "test" { Invoke-Test }
    "test-verbose" { Invoke-TestVerbose }
    "test-coverage" { Invoke-TestCoverage }
    "run" { Invoke-Run }
    "clean" { Invoke-Clean }
    "help" { Show-Help }
    default { Show-Help }
}
