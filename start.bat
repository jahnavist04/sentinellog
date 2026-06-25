@echo off
echo Starting SentinelLog...

start "Collector" cmd /k "cd /d C:\Users\thippeswamy\OneDrive\Desktop\sentinellog\collector && python server.py"

timeout /t 3 /nobreak >nul

start "Backend" cmd /k "cd /d C:\Users\thippeswamy\OneDrive\Desktop\sentinellog\dashboard\backend && python app.py"

timeout /t 3 /nobreak >nul

start "ServiceA" cmd /k "cd /d C:\Users\thippeswamy\OneDrive\Desktop\sentinellog\services && set SERVICE_NAME=ServiceA && python service.py"

start "ServiceB" cmd /k "cd /d C:\Users\thippeswamy\OneDrive\Desktop\sentinellog\services && set SERVICE_NAME=ServiceB && python service.py"

start "ServiceC" cmd /k "cd /d C:\Users\thippeswamy\OneDrive\Desktop\sentinellog\services && set SERVICE_NAME=ServiceC && python service.py"

timeout /t 2 /nobreak >nul

start "Frontend" cmd /k "cd /d C:\Users\thippeswamy\OneDrive\Desktop\sentinellog\dashboard\frontend && npm run dev"

echo All services started! Open http://localhost:5173