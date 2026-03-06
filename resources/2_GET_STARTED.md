# Get Ready

## Prerequisites
- Node.js 18+ and npm
- Python 3.10+

## Version Managers
If you do not have the right versions, use a version manager.

### Install pyenv (macOS)
```bash
brew install pyenv
```

### Install nvm (macOS)
```bash
brew install nvm
mkdir -p ~/.nvm
export NVM_DIR="$HOME/.nvm"
source $(brew --prefix nvm)/nvm.sh
```
Add the lines above to your shell profile (e.g. `~/.zshrc`) so they load automatically:
```bash
printf '\nexport NVM_DIR="$HOME/.nvm"\nsource $(brew --prefix nvm)/nvm.sh\n' >> ~/.zshrc
```
Note: reload your shell (or open a new terminal) so `nvm` is available.

## Install Runtimes
### Python (pyenv)
```bash
pyenv install 3.10.14
pyenv local 3.10.14
python --version
```

### Node (nvm)
```bash
nvm install 18
nvm use 18
node --version
```

## Backend (Flask) Setup
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Frontend (Vite + React) Setup
```bash
cd frontend
npm install
```
