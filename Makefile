.PHONY: help setup install run test clean build docker

SYSTEM_NAME := selfaware-ai-v100
PYTHON := python3
PIP := pip3
DOCKER := docker

help: ## Show this help message
	@echo "Self-Aware AI System v100 - Commands"
	@echo "===================================="
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Setup complete system
	@echo "🚀 Setting up Self-Aware AI System v100..."
	$(PIP) install -r requirements.txt
	mkdir -p data logs backups snapshots visualizations
	python config.py --create-configs
	@echo "✅ Setup complete!"

install: setup ## Install system

run: ## Run the system
	@echo "🚀 Starting Self-Aware AI System..."
	$(PYTHON) main.py

test: ## Run tests
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=.

clean: ## Clean logs and temp files
	@echo "🧹 Cleaning..."
	rm -rf logs/*.log
	rm -rf data/*.db
	rm -rf __pycache__ **/__pycache__

build: ## Build Docker image
	@echo "📦 Building Docker image..."
	$(DOCKER) build -t $(SYSTEM_NAME):latest .

docker-run: build ## Run in Docker
	@echo "🐳 Running in Docker..."
	$(DOCKER) run -d \
		-p 8080:8080 -p 8081:8081 \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		--name $(SYSTEM_NAME) \
		$(SYSTEM_NAME):latest

stop: ## Stop system
	@echo "🛑 Stopping system..."
	pkill -f "python main.py" || true
	$(DOCKER) stop $(SYSTEM_NAME) || true

emergency-test: ## Simulate emergency (Feature 1)
	$(PYTHON) -c "import asyncio; from main import SelfAwareAISystem; s=SelfAwareAISystem(); asyncio.run(s.simulate_emergency())"

benchmark: ## Run benchmark (Feature 2)
	$(PYTHON) -c "import asyncio; from main import SelfAwareAISystem; s=SelfAwareAISystem(); print(asyncio.run(s.benchmark_consciousness()))"

list-features: ## List all features
	python config.py --list-features

enable-feature: ## Enable feature (usage: make enable-feature FEATURE=name)
	python config.py --enable $(FEATURE)

disable-feature: ## Disable feature (usage: make disable-feature FEATURE=name)
	python config.py --disable $(FEATURE)

dev-server: ## Development server
	uvicorn main:app --reload --port 8080 --log-level info

monitor: ## Start monitoring dashboard
	open monitoring_dashboard.html
	python -m http.server 8083

all: setup run ## Full setup and run
