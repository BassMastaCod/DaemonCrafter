@echo off
set LOGS_DIR=logs
set EXE_FILE=daemoncrafter_test.exe
set XML_FILE=daemoncrafter_test.xml

echo Deleting logs directory: %LOGS_DIR%
if exist %LOGS_DIR% (
    rmdir /s /q %LOGS_DIR%
) else (
    echo Logs directory does not exist.
)

echo Deleting executable file: %EXE_FILE%
if exist %EXE_FILE% (
    del /q %EXE_FILE%
) else (
    echo Executable file does not exist.
)

echo Deleting XML configuration file: %XML_FILE%
if exist %XML_FILE% (
    del /q %XML_FILE%
) else (
    echo XML configuration file does not exist.
)

echo Cleanup completed successfully.
