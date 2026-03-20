@echo off
set SERVICE_NAME=daemoncrafter_test

echo Stopping service: %SERVICE_NAME%
sc stop %SERVICE_NAME%
if %ERRORLEVEL% NEQ 0 (
    echo Service %SERVICE_NAME% is not running or couldn't be stopped.
)

echo Deleting service: %SERVICE_NAME%
sc delete %SERVICE_NAME%
if %ERRORLEVEL% NEQ 0 (
    echo Service %SERVICE_NAME% is not installed or couldn't be deleted.
)

echo Service removed successfully.
