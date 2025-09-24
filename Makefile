# LSL Stream Receiver - Makefile
# ===============================
#
# This Makefile automates common development and usage tasks for the LSL Stream Receiver.
#
# Usage:
#   make help          # Show this help message
#   make setup         # Set up virtual environment and install dependencies
#   make app           # Start the Streamlit web application
#   make dev           # Start the app in development mode with hot reload
#   make examples      # Run example scripts
#   make test          # Run tests
#   make clean         # Clean up temporary files
#   make docs          # Generate documentation
#   make lint          # Run linting
#   make format        # Format code
#

.PHONY: help setup install app dev examples test clean docs lint format venv-check user-guide dev-guide architecture

# Default target
help:
	@echo "LSL Stream Receiver - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup         # Create venv, install dependencies, and setup for development"
	@echo "  make install       # Install dependencies in existing venv"
	@echo "  make venv-check    # Check if virtual environment exists"
	@echo ""
	@echo "Running the Application:"
	@echo "  make app           # Start the Streamlit web application"
	@echo "  make dev           # Start in development mode with hot reload"
	@echo "  make examples      # Run example scripts with menu"
	@echo ""
	@echo "Development:"
	@echo "  make test          # Run all tests"
	@echo "  make lint          # Run linting checks"
	@echo "  make format        # Format code with black"
	@echo "  make clean         # Clean up temporary files"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs          # Generate documentation"
	@echo "  make user-guide    # Open user guide"
	@echo "  make dev-guide     # Open development guide"
	@echo "  make architecture  # Open architecture guide"
	@echo ""
	@echo "Examples:"
	@echo "  make example-basic        # Run basic receiver example"
	@echo "  make example-csv         # Run CSV logging example"
	@echo "  make example-plotter     # Run real-time plotter example"
	@echo "  make example-lab-study   # Run lab study collector example"

# Virtual environment setup
VENV_NAME := venv
PYTHON := python3
PIP := $(VENV_NAME)/bin/pip
PYTHON_VENV := $(VENV_NAME)/bin/python

# Check if we're in a virtual environment
VENV_CHECK := @if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "⚠️  Warning: Not running in virtual environment"; \
		echo "   Run 'source $(VENV_NAME)/bin/activate' first or use 'make setup'"; \
		echo ""; \
	fi

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Setup virtual environment and install dependencies
setup: venv-check
	@echo "$(GREEN)Setting up virtual environment and dependencies...$(NC)"
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "$(GREEN)Virtual environment created.$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"
	@echo ""
	@echo "$(YELLOW)To activate the virtual environment, run:$(NC)"
	@echo "  source $(VENV_NAME)/bin/activate"
	@echo ""
	@echo "$(YELLOW)To start the app, run:$(NC)"
	@echo "  make app"

# Check if virtual environment exists
venv-check:
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)Virtual environment not found.$(NC)"; \
		echo "$(GREEN)Creating virtual environment...$(NC)"; \
		$(PYTHON) -m venv $(VENV_NAME); \
		echo "$(GREEN)Virtual environment created.$(NC)"; \
	fi

# Install dependencies only
install: venv-check
	@echo "$(GREEN)Installing/updating dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependencies updated successfully!$(NC)"

# Start the Streamlit web application
app: venv-check
	@echo "$(GREEN)Starting LSL Stream Receiver web application...$(NC)"
	$(VENV_CHECK)
	$(PYTHON_VENV) -m streamlit run streamlit_app/app.py

# Start in development mode with hot reload
dev: venv-check
	@echo "$(GREEN)Starting LSL Stream Receiver in development mode...$(NC)"
	$(VENV_CHECK)
	$(PYTHON_VENV) -m streamlit run streamlit_app/app.py --server.headless true --server.port 8501

# Example runner with menu
examples: venv-check
	@echo "$(GREEN)LSL Stream Receiver - Examples$(NC)"
	@echo "================================"
	@echo ""
	@echo "Select an example to run:"
	@echo "1) Basic Receiver        - Simple data reception from all streams"
	@echo "2) CSV Logger           - Log data to CSV with metadata"
	@echo "3) Real-time Plotter    - Live visualization of stream data"
	@echo "4) Lab Study Collector  - Complete research study workflow"
	@echo "5) List LSL Streams     - Show available streams"
	@echo ""
	@echo "Or press Ctrl+C to exit"
	@echo ""
	@read -p "Enter choice (1-5): " choice; \
	case $$choice in \
		1) echo "$(GREEN)Running Basic Receiver Example...$(NC)"; \
		   $(PYTHON_VENV) examples/basic_receiver.py ;; \
		2) echo "$(GREEN)Running CSV Logger Example...$(NC)"; \
		   $(PYTHON_VENV) examples/csv_logger.py ;; \
		3) echo "$(GREEN)Running Real-time Plotter Example...$(NC)"; \
		   $(PYTHON_VENV) examples/real_time_plotter.py ;; \
		4) echo "$(GREEN)Running Lab Study Collector Example...$(NC)"; \
		   $(PYTHON_VENV) examples/lab_study_collector.py --help ;; \
		5) echo "$(GREEN)Listing Available LSL Streams...$(NC)"; \
		   $(PYTHON_VENV) -c "from pylsl import resolve_streams; streams = resolve_streams(); [print(f'- {s.name()}: {s.type()} ({s.nominal_srate()} Hz)') for s in streams] or print('No streams found')" ;; \
		*) echo "$(RED)Invalid choice. Please select 1-5.$(NC)" ;; \
	esac

# Individual example targets
example-basic: venv-check
	@echo "$(GREEN)Running Basic Receiver Example...$(NC)"
	$(PYTHON_VENV) examples/basic_receiver.py

example-csv: venv-check
	@echo "$(GREEN)Running CSV Logger Example...$(NC)"
	$(PYTHON_VENV) examples/csv_logger.py

example-plotter: venv-check
	@echo "$(GREEN)Running Real-time Plotter Example...$(NC)"
	$(PYTHON_VENV) examples/real_time_plotter.py

example-lab-study: venv-check
	@echo "$(GREEN)Running Lab Study Collector Example...$(NC)"
	$(PYTHON_VENV) examples/lab_study_collector.py --help

# Run tests
test: venv-check
	@echo "$(GREEN)Running tests...$(NC)"
	$(VENV_CHECK)
	@if [ -d "tests" ]; then \
		$(PYTHON_VENV) -m pytest tests/ -v; \
	else \
		echo "$(YELLOW)No tests directory found. Creating basic test structure...$(NC)"; \
		mkdir -p tests; \
		echo "# Add your tests here" > tests/__init__.py; \
		echo "def test_example():" > tests/test_example.py; \
		echo "    \"\"\"Example test\"\"\"" > tests/test_example.py; \
		echo "    assert True" >> tests/test_example.py; \
		echo "$(GREEN)Test structure created. Run 'make test' to execute.$(NC)"; \
	fi

# Clean up temporary files
clean:
	@echo "$(GREEN)Cleaning up temporary files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name "*.pyd" -delete 2>/dev/null || true
	@find . -name ".coverage" -delete 2>/dev/null || true
	@find . -name "coverage.xml" -delete 2>/dev/null || true
	@find . -name "*.log" -delete 2>/dev/null || true
	@find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed.$(NC)"

# Clean everything including virtual environment
clean-all: clean
	@echo "$(YELLOW)Removing virtual environment...$(NC)"
	@rm -rf $(VENV_NAME)
	@echo "$(GREEN)Complete cleanup finished.$(NC)"

# Generate documentation
docs: venv-check
	@echo "$(GREEN)Generating documentation...$(NC)"
	@if command -v mkdocs >/dev/null 2>&1; then \
		echo "$(GREEN)Using MkDocs...$(NC)"; \
		mkdocs build; \
	elif command -v sphinx-build >/dev/null 2>&1; then \
		echo "$(GREEN)Using Sphinx...$(NC)"; \
		sphinx-build docs/ docs/_build; \
	else \
		echo "$(YELLOW)No documentation generator found.$(NC)"; \
		echo "$(GREEN)Creating simple HTML documentation...$(NC)"; \
		echo "<html><head><title>LSL Stream Receiver Docs</title></head><body>" > docs/index.html; \
		echo "<h1>LSL Stream Receiver Documentation</h1>" >> docs/index.html; \
		cat docs/README.md | markdown >> docs/index.html 2>/dev/null || \
		echo "<pre>$(cat docs/README.md)</pre>" >> docs/index.html; \
		echo "</body></html>" >> docs/index.html; \
		echo "$(GREEN)Basic HTML documentation created at docs/index.html$(NC)"; \
	fi

# Run linting
lint: venv-check
	@echo "$(GREEN)Running linting checks...$(NC)"
	$(VENV_CHECK)
	@if command -v flake8 >/dev/null 2>&1; then \
		echo "$(GREEN)Running flake8...$(NC)"; \
		flake8 lsl_receiver/ streamlit_app/ examples/ --max-line-length=100 --exclude=__pycache__; \
	else \
		echo "$(YELLOW)flake8 not found. Install with: pip install flake8$(NC)"; \
	fi
	@if command -v pylint >/dev/null 2>&1; then \
		echo "$(GREEN)Running pylint...$(NC)"; \
		pylint lsl_receiver/ streamlit_app/ examples/ --disable=C,R,W0613,W0102; \
	else \
		echo "$(YELLOW)pylint not found. Install with: pip install pylint$(NC)"; \
	fi

# Format code
format: venv-check
	@echo "$(GREEN)Formatting code...$(NC)"
	$(VENV_CHECK)
	@if command -v black >/dev/null 2>&1; then \
		echo "$(GREEN)Running black...$(NC)"; \
		black lsl_receiver/ streamlit_app/ examples/ --line-length 100; \
	else \
		echo "$(YELLOW)black not found. Install with: pip install black$(NC)"; \
		echo "$(YELLOW)Skipping code formatting.$(NC)"; \
	fi

# Development setup with all tools
dev-setup: setup
	@echo "$(GREEN)Installing development tools...$(NC)"
	$(PIP) install black flake8 pylint pytest pytest-cov sphinx mkdocs
	@echo "$(GREEN)Development tools installed!$(NC)"

# Quick health check
health: venv-check
	@echo "$(GREEN)Running health check...$(NC)"
	$(VENV_CHECK)
	@echo "$(GREEN)Checking Python environment...$(NC)"
	$(PYTHON_VENV) -c "import sys; print(f'Python {sys.version}')"
	@echo "$(GREEN)Checking LSL installation...$(NC)"
	$(PYTHON_VENV) -c "import pylsl; print(f'LSL version: {pylsl.__version__}')"
	@echo "$(GREEN)Checking available streams...$(NC)"
	$(PYTHON_VENV) -c "from pylsl import resolve_streams; streams = resolve_streams(); print(f'Found {len(streams)} LSL streams')" 2>/dev/null || echo "No streams found (this is normal)"
	@echo "$(GREEN)Health check completed!$(NC)"

# Create requirements files for different use cases
requirements-dev: venv-check
	@echo "$(GREEN)Generating development requirements...$(NC)"
	@echo "# Development requirements for LSL Stream Receiver" > requirements-dev.txt
	@echo "-r requirements.txt" >> requirements-dev.txt
	@echo "black>=22.0.0" >> requirements-dev.txt
	@echo "flake8>=4.0.0" >> requirements-dev.txt
	@echo "pylint>=2.12.0" >> requirements-dev.txt
	@echo "pytest>=6.2.0" >> requirements-dev.txt
	@echo "pytest-cov>=2.12.0" >> requirements-dev.txt
	@echo "sphinx>=4.0.0" >> requirements-dev.txt
	@echo "mkdocs>=1.2.0" >> requirements-dev.txt
	@echo "" >> requirements-dev.txt
	@echo "# Optional: For documentation" >> requirements-dev.txt
	@echo "sphinx-rtd-theme>=1.0.0" >> requirements-dev.txt
	@echo "mkdocs-material>=8.0.0" >> requirements-dev.txt

# Docker build (if needed)
docker-build:
	@echo "$(GREEN)Building Docker image...$(NC)"
	@if command -v docker >/dev/null 2>&1; then \
		docker build -t lsl-stream-receiver .; \
		echo "$(GREEN)Docker image built successfully!$(NC)"; \
	else \
		echo "$(RED)Docker not found. Install Docker first.$(NC)"; \
	fi

# Show project status
status:
	@echo "$(GREEN)LSL Stream Receiver - Project Status$(NC)"
	@echo "====================================="
	@echo ""
	@echo "Virtual Environment:"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "  ✅ $(VENV_NAME)/ exists"; \
	else \
		echo "  ❌ $(VENV_NAME)/ not found"; \
	fi
	@echo ""
	@echo "Core Components:"
	@for dir in lsl_receiver streamlit_app examples docs tests; do \
		if [ -d "$$dir" ]; then \
			echo "  ✅ $$dir/"; \
		else \
			echo "  ❌ $$dir/"; \
		fi \
	done
	@echo ""
	@echo "Files:"
	@for file in requirements.txt Makefile; do \
		if [ -f "$$file" ]; then \
			echo "  ✅ $$file"; \
		else \
			echo "  ❌ $$file"; \
		fi \
	done
	@echo ""
	@echo "Ready to use: $(GREEN)make app$(NC) or $(GREEN)make examples$(NC)"

# Documentation targets
user-guide: venv-check
	@echo "$(GREEN)Opening User Guide...$(NC)"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open docs/user_guide.md; \
	elif command -v open >/dev/null 2>&1; then \
		open docs/user_guide.md; \
	elif command -v start >/dev/null 2>&1; then \
		start docs/user_guide.md; \
	else \
		echo "$(YELLOW)Please open docs/user_guide.md in your browser$(NC)"; \
	fi

dev-guide: venv-check
	@echo "$(GREEN)Opening Development Guide...$(NC)"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open docs/development.md; \
	elif command -v open >/dev/null 2>&1; then \
		open docs/development.md; \
	elif command -v start >/dev/null 2>&1; then \
		start docs/development.md; \
	else \
		echo "$(YELLOW)Please open docs/development.md in your browser$(NC)"; \
	fi

architecture: venv-check
	@echo "$(GREEN)Opening Architecture Guide...$(NC)"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open docs/architecture.md; \
	elif command -v open >/dev/null 2>&1; then \
		open docs/architecture.md; \
	elif command -v start >/dev/null 2>&1; then \
		start docs/architecture.md; \
	else \
		echo "$(YELLOW)Please open docs/architecture.md in your browser$(NC)"; \
	fi

# Default target when just running 'make'
all: setup
	@echo "$(GREEN)Setup complete! Run '$(YELLOW)make app$(GREEN)' to start the application.$(NC)"
