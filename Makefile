.PHONY: help start stop backend frontend install clean logs logs-backend logs-frontend

# Default target
help:
	@echo "SpendSense - Development Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make install        - Install all dependencies (backend + frontend)"
	@echo "  make start          - Start both servers in background"
	@echo "  make stop           - Stop all running servers"
	@echo "  make logs           - View logs from both servers"
	@echo "  make logs-backend   - View backend logs only"
	@echo "  make logs-frontend  - View frontend logs only"
	@echo "  make backend        - Start only backend (foreground)"
	@echo "  make frontend       - Start only frontend (foreground)"
	@echo "  make clean          - Clean build artifacts and caches"
	@echo ""

# Install dependencies
install:
	@echo "Installing backend dependencies..."
	cd spendsense-backend && uv sync
	@echo ""
	@echo "Installing frontend dependencies..."
	cd spendsense-frontend && bun install
	@echo ""
	@echo "✅ All dependencies installed!"

# Start both servers
start:
	@echo "Starting SpendSense..."
	@echo ""
	@echo "Starting backend server in background..."
	@bash -c 'cd spendsense-backend && uv run uvicorn spendsense.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 & echo $$! > ../backend.pid'
	@sleep 2
	@if [ -f backend.pid ]; then \
		echo "✅ Backend started (PID: $$(cat backend.pid))"; \
	else \
		echo "⚠️  Backend PID not captured, but server may be running"; \
	fi
	@echo ""
	@echo "Starting frontend server in background..."
	@bash -c 'cd spendsense-frontend && bun run dev -- --host --port 5173 > ../frontend.log 2>&1 & echo $$! > ../frontend.pid'
	@sleep 2
	@if [ -f frontend.pid ]; then \
		echo "✅ Frontend started (PID: $$(cat frontend.pid))"; \
	else \
		echo "⚠️  Frontend PID not captured, but server may be running"; \
	fi
	@echo ""
	@echo "Servers are running:"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - Backend Docs: http://localhost:8000/docs"
	@echo "  - Frontend App: http://localhost:5173"
	@echo ""
	@echo "View logs:"
	@echo "  - make logs (both servers)"
	@echo "  - make logs-backend"
	@echo "  - make logs-frontend"
	@echo ""
	@echo "Stop servers: make stop"

# Start backend server
backend:
	@echo "Starting backend server..."
	cd spendsense-backend && uv run uvicorn spendsense.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend server
frontend:
	@echo "Starting frontend server..."
	cd spendsense-frontend && bun run dev -- --host --port 5173

# Stop all servers
stop:
	@echo "Stopping all servers..."
	@if [ -f backend.pid ]; then \
		kill $$(cat backend.pid) 2>/dev/null || true; \
		rm backend.pid; \
		echo "✅ Backend stopped"; \
	fi
	@if [ -f frontend.pid ]; then \
		kill $$(cat frontend.pid) 2>/dev/null || true; \
		rm frontend.pid; \
		echo "✅ Frontend stopped"; \
	fi
	@pkill -f "uvicorn spendsense.main:app" 2>/dev/null || true
	@pkill -f "bun.*dev.*5173" 2>/dev/null || true
	@echo "✅ All servers stopped"

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf spendsense-backend/.venv
	rm -rf spendsense-backend/__pycache__
	rm -rf spendsense-backend/**/__pycache__
	rm -rf spendsense-frontend/node_modules
	rm -rf spendsense-frontend/.svelte-kit
	rm -rf spendsense-frontend/build
	rm -f backend.log frontend.log backend.pid frontend.pid
	@echo "✅ Clean complete"

# View logs
logs:
	@echo "Showing logs (Ctrl+C to exit)..."
	@tail -f backend.log frontend.log

# View backend logs only
logs-backend:
	@tail -f backend.log

# View frontend logs only
logs-frontend:
	@tail -f frontend.log
