# AI Tools
ai-generate: ## Generate text with LLM
	@curl -X POST http://localhost:8080/api/ai/generate \
		-H "Content-Type: application/json" \
		-d '{"prompt": "$(PROMPT)", "provider": "$(PROVIDER)"}'

ai-embed: ## Embed text
	@curl -X POST http://localhost:8080/api/ai/embed \
		-H "Content-Type: application/json" \
		-d '{"text": "$(TEXT)", "provider": "$(PROVIDER)"}'

vector-store: ## Store document in vector DB
	@curl -X POST http://localhost:8080/api/vector/store \
		-H "Content-Type: application/json" \
		-d '{"content": "$(CONTENT)", "metadata": {"source": "cli"}}'

vector-search: ## Search vector DB
	@curl -X POST http://localhost:8080/api/vector/search \
		-H "Content-Type: application/json" \
		-d '{"query": "$(QUERY)", "limit": $(LIMIT)}'

# Workflow
start-celery: ## Start Celery worker
	@celery -A src.celery_app worker --loglevel=info --concurrency=4

start-celery-beat: ## Start Celery beat
	@celery -A src.celery_app beat --loglevel=info

# Monitoring
start-prometheus: ## Start Prometheus
	@docker-compose up -d prometheus

start-grafana: ## Start Grafana
	@docker-compose up -d grafana

# Documentation
docs-serve: ## Serve MkDocs
	@mkdocs serve --dev-addr 0.0.0.0:8084

# Security
security-scan: ## Run full security scan
	@bandit -r src/ -f json -o reports/security/bandit.json
	@safety check --json -o reports/security/safety.json
	@trivy fs --format json -o reports/security/trivy.json .
