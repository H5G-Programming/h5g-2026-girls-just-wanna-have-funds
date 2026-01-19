# Running Locally

## Prerequisites
- Node.js 18+ and npm
- Python 3.10+

## Install Python and Node
If you do not have the right versions, use a version manager.

### Python (pyenv)
```bash
# Install pyenv (macOS)
brew install pyenv

# Install and use Python 3.10
pyenv install 3.10.14
pyenv local 3.10.14
python --version
```

### Node (nvm)
```bash
# Install nvm (macOS)
brew install nvm
mkdir -p ~/.nvm
export NVM_DIR=\"$HOME/.nvm\"
source $(brew --prefix nvm)/nvm.sh

# Install and use Node 18
nvm install 18
nvm use 18
node --version
```

## Backend (Flask)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

The backend should be available at:
- http://localhost:5000

## Frontend (Vite + React)
```bash
cd frontend
npm install
npm run dev
```

The frontend should be available at:
- http://localhost:5173

## Configuration
- The frontend expects the backend at `http://localhost:5000`.
- If you change ports, update the frontend API base URL accordingly.
