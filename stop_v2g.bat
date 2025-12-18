@echo off
REM V2G Platform Stop Script
REM This script stops all V2G platform services
REM Usage: Just double-click this file

powershell -ExecutionPolicy Bypass -File "./stop_v2g.ps1"
pause