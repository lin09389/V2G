# V2G Platform Startup Script
# This script ensures all dependencies are installed and starts both backend and frontend services
# Usage: .\start_v2g.ps1 [start|stop]

param(
    [Parameter(Position=0)]
    [ValidateSet("start", "stop")]
    [string]$Command = "start"
)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "V2G Platform Startup Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "[BACKEND] API: http://localhost:5000" -ForegroundColor White
Write-Host "[FRONTEND] Page: http://localhost:8001/index.html" -ForegroundColor White
Write-Host "[API DOCS] Swagger: http://localhost:5000/docs" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "=========================================" -ForegroundColor Cyan

# Change to project directory
Set-Location "$PSScriptRoot"

# Function to install dependencies
function Install-Dependencies {
    Write-Host "\nChecking Python dependencies..." -ForegroundColor Yellow
    
    # Check if pip is available
    try {
        $pipVersion = python -m pip --version
        Write-Host "[OK] pip is installed: $pipVersion" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] pip is not available. Please install Python with pip." -ForegroundColor Red
        exit 1
    }
    
    # Install backend dependencies
    Write-Host "\nInstalling backend dependencies..." -ForegroundColor Yellow
    try {
        python -m pip install -r "backend/requirements.txt"
        Write-Host "[OK] Backend dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Failed to install backend dependencies" -ForegroundColor Red
        exit 1
    }
}

# Function to start services
function Start-Services {
    # Install dependencies first
    Install-Dependencies

    # Start backend service
    Write-Host "\nStarting Backend Service..." -ForegroundColor Yellow
    $backendJob = Start-Job -ScriptBlock {
        Set-Location "$using:PSScriptRoot/backend"
        python -m uvicorn app:app --reload --host 0.0.0.0 --port 5000
    }

    # Wait for backend to start
    Write-Host "Waiting for backend to initialize..." -ForegroundColor White
    Start-Sleep -Seconds 5

    # Check if backend started successfully
    $backendStatus = Get-Job -Id $backendJob.Id
    if ($backendStatus.State -eq "Running") {
        Write-Host "[OK] Backend service started successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Backend service failed to start" -ForegroundColor Red
        Receive-Job -Id $backendJob.Id
        exit 1
    }

    # Start frontend service
    Write-Host "\nStarting Frontend Service..." -ForegroundColor Yellow
    $frontendJob = Start-Job -ScriptBlock {
        Set-Location "$using:PSScriptRoot/frontend"
        python -m http.server 8001
    }

    # Wait for frontend to start
    Write-Host "Waiting for frontend to initialize..." -ForegroundColor White
    Start-Sleep -Seconds 2

    # Check if frontend started successfully
    $frontendStatus = Get-Job -Id $frontendJob.Id
    if ($frontendStatus.State -eq "Running") {
        Write-Host "[OK] Frontend service started successfully" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Frontend service failed to start" -ForegroundColor Red
        Receive-Job -Id $frontendJob.Id
        # Cleanup backend
        Stop-Job -Job $backendJob
        Remove-Job -Job $backendJob
        exit 1
    }

    # Show startup info
    Write-Host "`n=========================================" -ForegroundColor Green
    Write-Host "SUCCESS: V2G Platform Started Successfully!" -ForegroundColor Green
    Write-Host "=========================================" -ForegroundColor Green
    Write-Host "[BACKEND] API: http://localhost:5000" -ForegroundColor White
    Write-Host "[FRONTEND] Page: http://localhost:8001/index.html" -ForegroundColor White
    Write-Host "[API DOCS] Swagger: http://localhost:5000/docs" -ForegroundColor White
    Write-Host "=========================================" -ForegroundColor Green

    Write-Host "`nIMPORTANT NOTES:" -ForegroundColor Yellow
    Write-Host "- Press Ctrl+C at any time to stop all services" -ForegroundColor White
    Write-Host "- Run '.\start_v2g.ps1 stop' to stop all services from another terminal" -ForegroundColor White
    Write-Host "- Backend is running in development mode (auto-reload enabled)" -ForegroundColor White
    Write-Host "- Frontend is served by Python's built-in HTTP server" -ForegroundColor White

    # Wait for user interrupt
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } catch [System.Management.Automation.KeyboardInterrupt] {
        Write-Host "`n`n=========================================" -ForegroundColor Yellow
        Write-Host "Stopping all services..." -ForegroundColor Yellow
        
        # Stop backend service
        Stop-Job -Job $backendJob
        Remove-Job -Job $backendJob
        Write-Host "[STOPPED] Backend service stopped" -ForegroundColor Red
        
        # Stop frontend service
        Stop-Job -Job $frontendJob
        Remove-Job -Job $frontendJob
        Write-Host "[STOPPED] Frontend service stopped" -ForegroundColor Red
        
        Write-Host "`nSUCCESS: All services stopped successfully!" -ForegroundColor Green
        Write-Host "=========================================" -ForegroundColor Cyan
    }
}

# Function to stop services
function Stop-Services {
    Write-Host "`n=========================================" -ForegroundColor Yellow
    Write-Host "Stopping V2G Platform Services..." -ForegroundColor Yellow
    Write-Host "=========================================" -ForegroundColor Yellow

    $stoppedProcesses = 0
    $stoppedJobs = 0

    # 1. Stop PowerShell jobs that were created when starting services
    try {
        $jobs = Get-Job -State Running -ErrorAction SilentlyContinue
        foreach ($job in $jobs) {
            # Get the job's command to identify our project jobs
            $jobCommand = $job.Command
            if ($jobCommand -like "*uvicorn app:app*" -or $jobCommand -like "*http.server 8001*") {
                Stop-Job -Job $job
                Remove-Job -Job $job
                Write-Host "[STOPPED] V2G service job stopped (ID: $($job.Id))" -ForegroundColor Red
                $stoppedJobs++
            }
        }
    } catch {
        Write-Host "[INFO] Could not get or stop PowerShell jobs" -ForegroundColor Yellow
    }

    # 2. Find and stop only Python processes that belong to this project
    try {
        # Get all Python processes (supporting different Python versions like python, python3, python3.11)
        $pythonProcesses = Get-Process | Where-Object {$_.Name -like "python*"} | Where-Object {$_.Name -notlike "pythonw*"}
        
        if ($pythonProcesses) {
            foreach ($proc in $pythonProcesses) {
                try {
                    # Get the command line of the process to identify our project processes
                    $cmdLine = (Get-WmiObject Win32_Process -Filter "ProcessId = $($proc.Id)" -ErrorAction SilentlyContinue).CommandLine
                    
                    if ($cmdLine) {
                        # Check if the command line contains our project-specific commands
                        if ($cmdLine -like "*uvicorn app:app*" -or $cmdLine -like "*http.server 8001*") {
                            $proc.Kill()
                            $proc.WaitForExit()
                            Write-Host "[STOPPED] V2G Python process stopped (PID: $($proc.Id), Name: $($proc.Name))" -ForegroundColor Red
                            $stoppedProcesses++
                        }
                    }
                } catch {
                    continue
                }
            }
        }
    } catch {
        Write-Host "[INFO] Could not get process command line information" -ForegroundColor Yellow
    }

    if ($stoppedProcesses -eq 0 -and $stoppedJobs -eq 0) {
        Write-Host "`n[INFO] No V2G Platform services were found running" -ForegroundColor Yellow
    } else {
        Write-Host "`nSUCCESS: Stopped $stoppedProcesses V2G Python process(es) and $stoppedJobs job(s)!" -ForegroundColor Green
    }

    Write-Host "=========================================" -ForegroundColor Cyan
}

# Main script logic
switch ($Command) {
    "start" {
        Start-Services
    }
    "stop" {
        Stop-Services
    }
    default {
        Write-Host "[ERROR] Unknown command: $Command" -ForegroundColor Red
        Write-Host "Usage: .\start_v2g.ps1 [start|stop]" -ForegroundColor White
        exit 1
    }
}
