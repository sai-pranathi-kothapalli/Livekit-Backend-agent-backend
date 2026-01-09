"""
Agent Web Service Wrapper

This allows the agent to run as a Render Web Service (free tier)
instead of requiring a Background Worker (paid tier).

It starts the agent in a background thread and runs a simple HTTP server
for health checks to keep the service alive.
"""

import threading
import sys
import os
from fastapi import FastAPI
import uvicorn
from app.config import get_config
from app.utils.logger import get_logger

# Import agent components
from app.agents.entrypoint import entrypoint
from livekit import agents

logger = get_logger(__name__)
config = get_config()

# Create FastAPI app for health checks
app = FastAPI(title="LiveKit Agent Worker", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "ok",
        "service": "livekit-agent-worker",
        "agent_name": config.livekit.agent_name,
        "message": "Agent worker is running"
    }

@app.get("/healthz")
async def healthz():
    """Health check endpoint for Render"""
    return {"status": "ok", "service": "livekit-agent-worker"}

def run_agent():
    """Run the agent worker in a background thread"""
    try:
        logger.info("=" * 60)
        logger.info("🔧 AGENT WORKER STARTING")
        logger.info("=" * 60)
        logger.info(f"   Agent Name: '{config.livekit.agent_name}'")
        logger.info(f"   Status: Registering with LiveKit Cloud...")
        logger.info(f"   Waiting for job dispatch...")
        logger.info("=" * 60)
        
        # Set sys.argv for agent CLI
        original_argv = sys.argv.copy()
        sys.argv = [sys.argv[0], 'dev']
        
        # Run the agent
        agents.cli.run_app(agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name=config.livekit.agent_name,
        ))
    except Exception as e:
        logger.error(f"Agent worker error: {e}", exc_info=True)
    finally:
        sys.argv = original_argv

if __name__ == "__main__":
    # Start agent in background thread
    agent_thread = threading.Thread(target=run_agent, daemon=True)
    agent_thread.start()
    
    logger.info("✅ Agent worker started in background thread")
    logger.info("🌐 Starting HTTP server for health checks...")
    
    # Get port from environment (Render provides $PORT)
    port = int(os.environ.get("PORT", 10000))
    
    # Run HTTP server (this blocks and keeps the service alive)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

