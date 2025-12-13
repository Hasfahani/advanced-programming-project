@echo off
:: Change to the directory where this batch file is located
cd /d "%~dp0"

echo ========================================
echo Starting Backend Server and Running Tests
echo ========================================
echo.

:: Start the backend server in the background
start "Backend Server" cmd /k "cd /d %~dp0backend & python app.py"

:: Wait for server to start
echo Waiting for server to start...
timeout /t 3 /nobreak >nul

:: Run the tests
echo.
echo Running tests...
python tests\test.py

echo.
echo ========================================
echo Tests completed! 
echo Close the Backend Server window when done.
echo ========================================
pause
