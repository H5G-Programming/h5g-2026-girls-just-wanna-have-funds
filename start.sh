#!/bin/bash
echo "=== Starting Priority Bank ==="
echo ""

# Start backend in the background
echo "--- Starting Backend (Flask) on port 5001 ---"
APP_FILE="${1:-app_needs_help.py}"
cd backend
uv run "$APP_FILE" &
BACKEND_PID=$!
cd ..

# Give backend a moment to start
sleep 1

# Start frontend
echo "--- Starting Frontend (Vite) on port 5173 ---"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== Priority Bank is running! ==="
echo "  Frontend: http://localhost:5173"
# echo "  Backend:  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both."

# When Ctrl+C is pressed, stop both processes
trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT

# Wait for both processes
wait
