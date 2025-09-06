# Nano Banana Hackathon

A full-stack application with Next.js frontend and FastAPI backend.

## Project Structure

```
nano-banana-hackathon/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── start.sh          # Shell script to start both servers
├── start.py          # Python script to start both servers
├── health.sh         # Health check script for both services
└── README.md
```

## Quick Start

### Option 1: Using the shell script (Unix/macOS)

```bash
./start.sh
```

### Option 2: Using the Python script (Cross-platform)

```bash
python start.py
```

### Option 3: Manual startup

1. **Start the backend:**

   ```bash
   cd backend
   source venv/bin/activate
   python main.py
   ```

2. **Start the frontend (in a new terminal):**
   ```bash
   cd frontend
   npm run dev
   ```

## Health Check

Check the status of both services:

```bash
./health.sh
```

This script will:

- ✅ Check if frontend is accessible at http://localhost:3000
- ✅ Check if backend is accessible at http://localhost:8000
- ✅ Test backend health endpoint
- ✅ Display detailed backend status information
- 🎨 Show colored output for easy status identification

## Access Points

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Development

### Backend (FastAPI)

- Virtual environment: `backend/venv/`
- Dependencies: `backend/requirements.txt`
- Main application: `backend/main.py`

### Frontend (Next.js)

- Dependencies: `frontend/node_modules/`
- Package configuration: `frontend/package.json`
- Source code: `frontend/src/`

## Features

- ✅ CORS enabled for frontend-backend communication
- ✅ TypeScript support in frontend
- ✅ Tailwind CSS for styling
- ✅ ESLint for code quality
- ✅ Hot reload for both frontend and backend
- ✅ Real-time backend status monitoring on frontend
- ✅ Health check endpoints for both services
- ✅ Automated health check script with colored output
