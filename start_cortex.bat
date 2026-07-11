@echo off
echo Starting CORTEX AI Leads Qualifier...

echo Starting API Server (Backend)...
start cmd /k "cd apps\api && .venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Starting Web Server (Frontend)...
start cmd /k "cd apps\web && npm run dev"

echo.
echo Both servers are starting up in separate windows!
echo --------------------------------------------------
echo The Web UI will be available at: http://localhost:3001
echo The API will be available at:    http://localhost:8000
echo.
echo You can keep this window open or close it.
pause
