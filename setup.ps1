# Quick Start Script for 4D-SynthForge
# This script helps you get started quickly

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  4D-SynthForge Setup Helper" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[2/5] Installing dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Some dependencies failed to install" -ForegroundColor Yellow
}

# Check for Gemini API key
Write-Host ""
Write-Host "[3/5] Checking Gemini API key..." -ForegroundColor Yellow
if ($env:GEMINI_API_KEY) {
    $keyPreview = $env:GEMINI_API_KEY.Substring(0, [Math]::Min(10, $env:GEMINI_API_KEY.Length)) + "..."
    Write-Host "  ✓ API key found: $keyPreview" -ForegroundColor Green
} else {
    Write-Host "  ✗ GEMINI_API_KEY not set!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Set your API key with:" -ForegroundColor Yellow
    Write-Host "    `$env:GEMINI_API_KEY = 'your-api-key-here'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Get your key from: https://aistudio.google.com" -ForegroundColor Yellow
    Write-Host ""
    
    $setNow = Read-Host "  Would you like to set it now? (y/n)"
    if ($setNow -eq 'y') {
        $apiKey = Read-Host "  Enter your Gemini API key"
        $env:GEMINI_API_KEY = $apiKey
        Write-Host "  ✓ API key set for this session" -ForegroundColor Green
        Write-Host "  (Note: This won't persist after closing PowerShell)" -ForegroundColor Yellow
    }
}

# Check for Isaac Sim (optional)
Write-Host ""
Write-Host "[4/5] Checking for Isaac Sim..." -ForegroundColor Yellow
$isaacPath = "$env:USERPROFILE\.local\share\ov\pkg"
if (Test-Path $isaacPath) {
    $isaacVersions = Get-ChildItem $isaacPath -Filter "isaac_sim-*" -Directory
    if ($isaacVersions.Count -gt 0) {
        $latest = $isaacVersions | Sort-Object Name | Select-Object -Last 1
        Write-Host "  ✓ Isaac Sim found: $($latest.Name)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Isaac Sim directory exists but no versions found" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠ Isaac Sim not found (optional)" -ForegroundColor Yellow
    Write-Host "    You can still use the pipeline without rendering" -ForegroundColor Gray
}

# Create demo video
Write-Host ""
Write-Host "[5/5] Creating demo video..." -ForegroundColor Yellow
if (Test-Path "examples\ball_cup.mp4") {
    Write-Host "  ✓ Demo video already exists" -ForegroundColor Green
} else {
    python demo_video_creator.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Demo video created" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Failed to create demo video" -ForegroundColor Yellow
    }
}

# Summary
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick commands:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Analyze video:" -ForegroundColor Cyan
Write-Host "     python video_analyzer.py examples\ball_cup.mp4" -ForegroundColor White
Write-Host ""
Write-Host "  2. Full pipeline (9 variations):" -ForegroundColor Cyan
Write-Host "     python main.py examples\ball_cup.mp4 --count 9" -ForegroundColor White
Write-Host ""
Write-Host "  3. Generate 100 variations:" -ForegroundColor Cyan
Write-Host "     python main.py examples\ball_cup.mp4 --count 100" -ForegroundColor White
Write-Host ""
Write-Host "For more info: See README.md" -ForegroundColor Gray
Write-Host ""
