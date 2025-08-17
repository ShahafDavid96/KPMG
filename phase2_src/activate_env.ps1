Write-Host "Activating virtual environment..." -ForegroundColor Green
Set-Location ..
& .\.venv\Scripts\Activate.ps1
Set-Location phase2_src
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Yellow
Write-Host "Python path: $env:PATH" -ForegroundColor Yellow
Write-Host "Ready to work!" -ForegroundColor Green
