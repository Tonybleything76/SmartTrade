# Multi-Agent AI Content System - Quick Commands

.PHONY: help install run web clean test logs

help:
	@echo "Multi-Agent AI Content System Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make run        - Start the complete system"
	@echo "  make web        - Start web interface only"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean temporary files"
	@echo "  make logs       - View system logs"
	@echo "  make setup      - Initial setup with environment"

install:
	pip install -e .

setup:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your API keys."; \
	else \
		echo ".env file already exists."; \
	fi
	@mkdir -p logs data
	@echo "Setup complete. Edit .env with your API keys, then run 'make run'"

run:
	python main.py

web:
	python -c "from web_interface import create_app; app = create_app(); app.run(host='0.0.0.0', port=5000, debug=False)"

test:
	python -m pytest tests/ -v

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf build dist *.egg-info

logs:
	@if [ -f logs/system.log ]; then \
		tail -f logs/system.log; \
	else \
		echo "No log file found. Start the system first with 'make run'"; \
	fi