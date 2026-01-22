# Running Locally

## Backend (Flask)
```bash
cd backend
source .venv/bin/activate
python3 app.py
```

The backend should be available at:
- http://localhost:5001

## Frontend (Vite + React)
```bash
cd frontend
npm run dev
```

The frontend should be available at:
- http://localhost:5173

## Configuration
- The frontend expects the backend at `http://localhost:5001`.
- If you change ports, update the frontend API base URL accordingly.
