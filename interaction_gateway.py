"""
Universal Interaction Gateway
Features 76-85: Advanced Interaction Interfaces
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

class UniversalInteractionGateway:
    """Multi-modal interaction gateway"""

    def __init__(self, system):
        self.system = system
        self.logger = logging.getLogger("InteractionGateway")
        self.app = FastAPI(title="SelfAwareAI API", version="100.0")
        self.websockets: List[WebSocket] = []

    async def initialize(self):
        """Initialize interaction gateway"""
        self.logger.info("💬 Initializing Universal Interaction Gateway...")
        self._setup_routes()

        # Start server
        asyncio.create_task(self._run_server())

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.post("/api/task")
        async def submit_task(task: Dict[str, Any]):
            self.system.submit_task(task)
            return {"status": "accepted", "task_id": task.get("id")}

        @self.app.get("/api/status")
        async def get_status():
            return {
                "system_id": self.system.system_id,
                "state": self.system.current_state.value,
                "consciousness": self.system.consciousness_layer.get_consciousness_summary(),
                "metrics": self.system.metrics[-1].__dict__ if self.system.metrics else {}
            }

        @self.app.websocket("/ws/monitoring")
        async def websocket_endpoint(websocket: WebSocket):
            await self._handle_websocket(websocket)

        @self.app.post("/api/emergency/simulate")
        async def simulate_emergency(scenario: Dict[str, str]):
            await self.system.simulate_emergency(scenario.get("scenario", "system_overload"))
            return {"status": "emergency_simulated"}

        @self.app.post("/api/consciousness/benchmark")
        async def benchmark_consciousness():
            result = await self.system.benchmark_consciousness()
            return result

    async def _run_server(self):
        """Run FastAPI server"""
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.system.config.interaction.rest_port
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def _handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection for real-time monitoring"""
        await websocket.accept()
        self.websockets.append(websocket)

        try:
            while True:
                data = await websocket.receive_text()
                await self._process_websocket_message(websocket, data)
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            self.websockets.remove(websocket)

    async def _process_websocket_message(self, websocket: WebSocket, message: str):
        """Process incoming WebSocket message"""
        try:
            data = json.loads(message)

            if data.get("type") == "get_consciousness_flow":
                flow_data = await self.system.monitoring_system.visualize_consciousness_flow()
                await websocket.send_json({
                    "type": "consciousness_flow",
                    "data": flow_data
                })

            elif data.get("type") == "submit_task":
                self.system.submit_task(data.get("task"))
                await websocket.send_json({"status": "accepted"})

        except json.JSONDecodeError:
            await websocket.send_json({"error": "Invalid JSON"})

    async def emit_update(self, data: Dict[str, Any]):
        """Emit update to all connected WebSockets"""
        message = json.dumps(data)

        for websocket in self.websockets:
            try:
                await websocket.send_text(message)
            except Exception as e:
                self.logger.error(f"Failed to send to websocket: {e}")
                self.websockets.remove(websocket)

    async def shutdown(self):
        """Shutdown gateway"""
        self.logger.info("🛑 Shutting down interaction gateway...")

        for websocket in self.websockets:
            await websocket.close()
