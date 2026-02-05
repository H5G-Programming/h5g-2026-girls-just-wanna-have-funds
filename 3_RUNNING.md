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

# Running in GitHub Codespaces
1. Open the repo in GitHub and click "Code" -> "Codespaces" -> "Create codespace on main".
2. Wait for the container to build and for dependencies to install.
3. In two terminals:
   - Backend: `python backend/app.py`
   - Frontend: `cd frontend && npm run dev`

Ports 5001 (API) and 5173 (web) will be forwarded automatically.
