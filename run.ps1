$ErrorActionPreference = "Stop"

$ProjectRoot = "d:\Projects\EVA"
$VenvPath = "$ProjectRoot\.venv"
$PythonExe = "$VenvPath\Scripts\python.exe"

Write-Host "🚀 Starting EVA System..." -ForegroundColor Cyan

# 1. Kill existing uvicorn and streamlit processes to free ports
Write-Host "🧹 Cleaning up existing processes on ports 8000 and 8502..."
$ports = @(8000, 8502)
foreach ($port in $ports) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        foreach ($conn in $connections) {
            $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "   Stopping process $($process.ProcessName) (PID: $($process.Id)) on port $port" -ForegroundColor Yellow
                Stop-Process -Id $process.Id -Force
            }
        }
    } catch {
        # Ignore errors if no process is bound
    }
}
Start-Sleep -Seconds 2

# 2. Check virtual environment
if (-Not (Test-Path $PythonExe)) {
    Write-Host "❌ Virtual environment not found at $VenvPath. Please follow STARTUP.md to set it up." -ForegroundColor Red
    exit 1
}

# 3. Start Backend (FastAPI) in the background
Write-Host "🌟 Starting Backend (FastAPI)..." -ForegroundColor Green
$BackendArgs = "-m", "uvicorn", "Backend.api.main:app", "--reload"
Start-Process -NoNewWindow -FilePath $PythonExe -ArgumentList $BackendArgs -WorkingDirectory $ProjectRoot
Write-Host "   Backend is running at http://localhost:8000"

# Wait a moment for backend to initialize
Start-Sleep -Seconds 5

# 4. Start Frontend (Streamlit)
Write-Host "🌟 Starting Frontend (Streamlit)..." -ForegroundColor Green
$FrontendArgs = "-m", "streamlit", "run", "Frontend\streamlit_app.py"
Start-Process -FilePath $PythonExe -ArgumentList $FrontendArgs -WorkingDirectory $ProjectRoot

Write-Host "✅ EVA System is now running!" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8502"
Write-Host "   Backend Docs: http://localhost:8000/docs"
Write-Host "Press Ctrl+C to stop the terminal (Note: background processes might need manual cleanup if not closed via the app)."
