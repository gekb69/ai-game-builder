# AI/ML Tools Documentation

## Vector Databases

### Weaviate
- **URL**: http://localhost:8083
- **Console**: http://localhost:8083/v1/console
- **Usage**: Semantic search with GraphQL

### Qdrant
- **URL**: http://localhost:6333
- **Dashboard**: http://localhost:6333/dashboard
- **Usage**: High-performance vector search

### Milvus
```yaml
# Add to docker-compose.yml
milvus:
  image: milvusdb/milvus:v2.3.3
  ports:
    - "19530:19530"

MLflow
URL: http://localhost:5000Track: Models, experiments, parametersCommand: mlflow ui --port 5000
Prometheus & Grafana
Prometheus: http://localhost:9090Grafana: http://localhost:3000(admin/admin)
Prefect & Dagster
Prefect
prefect server start --host 0.0.0.0 --port 4200

URL: http://localhost:4200
Dagster
dagster dev -f src/workflows.py

URL: http://localhost:3000
Sentry
# Add to main.py
import sentry_sdk
sentry_sdk.init(
    dsn=config.monitoring_tools.sentry.dsn,
    traces_sample_rate=1.0
)

OpenTelemetry
# Automatic instrumentation
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
SQLAlchemyInstrumentor().instrument()

DVC
# Initialize DVC
dvc init

# Add data
dvc add data/
dvc remote add -d s3://mybucket/selfaware-ai

# Push/pull
dvc push
dvc pull

BentoML
# src/bentoml_service.py
import bentoml
from bentoml.io import JSON

@bentoml.service(resources={"cpu": "2", "memory": "4Gi"})
class SelfAwareAIService:
    @bentoml.api(input=JSON(), output=JSON())
    async def process_task(self, task: dict) -> dict:
        system = SelfAwareAISystem()
        await system.initialize_system()
        system.submit_task(task)
        return {"status": "submitted"}

Security Tools
Bandit
bandit -r src/ -f json -o reports/security/bandit.json

Safety
safety check --json -o reports/security/safety.json

Trivy
trivy fs --format json -o reports/security/trivy.json .
trivy image -o reports/security/trivy-image.json selfaware-ai:latest

WebRTC (Optional)
# Add to requirements.txt
aiortc>=1.6.0

# Implementation in src/webrtc_gateway.py
class WebRTCInterface:
    async def handle_audio_stream(self, stream):
        # Real-time audio processing
        pass

Model Serving
vLLM (High-performance inference)
# Add to requirements.txt
vllm>=0.2.5

# Usage
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-2-7b-chat-hf \
  --tensor-parallel-size 2

Chinese Models
Kimi K2 (Moonshot)
# Implementation in src/kimi_provider.py
from moonshot import Moonshot

class KimiProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = Moonshot(api_key=api_key)

MiniMax M2
# Implementation in src/minimax_provider.py
from minimax import MiniMax

class MiniMaxProvider(LLMProvider):
    def __init__(self, api_key: str, group_id: str):
        self.client = MiniMax(api_key=api_key, group_id=group_id)
