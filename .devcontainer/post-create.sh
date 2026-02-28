#!/bin/bash
set -e

echo "=== Setting up Priority Bank ==="

# Backend setup
echo "--- Installing Python dependencies ---"
cd backend
pip install -r requirements.txt
cd ..

# Frontend setup
echo "--- Installing Node dependencies ---"
cd frontend
npm install
cd ..

echo "=== Setup complete! ==="
echo "To start the app:"
echo "  Backend:  cd backend && python app.py"
echo "  Frontend: cd frontend && npm run dev"
