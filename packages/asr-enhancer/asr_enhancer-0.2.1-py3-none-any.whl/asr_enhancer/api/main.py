"""
FastAPI Application
===================

Main FastAPI application for ASR Enhancement Layer.
Models are pre-loaded on startup for fast inference.

**GPU MODE IS DEFAULT** - Server requires GPU unless --cpu is specified.

Usage:
    # Default: GPU mode (fails if GPU not available)
    python -m asr_enhancer.api.main --keys "sk-asr-2024-prod-key-002-abc123"
    
    # Explicit CPU mode (override GPU default)
    python -m asr_enhancer.api.main --cpu --keys "sk-asr-2024-prod-key-002-abc123"
    
    # Dev key (expires after 2 hours)
    python -m asr_enhancer.api.main --keys "sk-asr-2024-prod-key-001-xyz789"
    
Note: Dev key (001) expires after 2 hours. Client keys (002-010) are valid forever.
"""

from __future__ import annotations

import os
import sys
import time
import subprocess
import argparse
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routes import router
from .enhance_endpoint import router as enhance_router
from .schemas import HealthResponse
from .api_keys import init_key_manager, get_key_manager
from ..utils import Config, load_config, setup_logging, get_logger

logger = get_logger(__name__)


# ============================================================================
# Global Settings (set via CLI args)
# ============================================================================

class ServerSettings:
    """Global server settings configured via CLI."""
    device: str = "cpu"  # "cpu" or "cuda"
    compute_type: str = "int8"  # "int8" for CPU, "float16" for GPU
    
settings = ServerSettings()


# ============================================================================
# Global Model Manager - Pre-loaded on startup
# ============================================================================

class ModelManager:
    """Holds pre-loaded models for fast inference."""
    
    def __init__(self):
        self.whisper_model = None
        self.llm_model = None
        self.llm_ready = False
        self.llm_provider = None
        self.llm_model_name = None
        self.device = "cpu"
        self.compute_type = "int8"
    
    def load_whisper(self, device: str = "cpu", compute_type: str = "int8"):
        """Load Whisper ASR model on specified device."""
        self.device = device
        self.compute_type = compute_type
        
        if self.whisper_model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(f"[1/2] Loading ASR model ({device.upper()})...")
                start = time.time()
                self.whisper_model = WhisperModel(
                    "large-v3",
                    device=device,
                    compute_type=compute_type
                )
                logger.info(f"✅ ASR loaded ({time.time() - start:.1f}s)")
            except ImportError as e:
                logger.warning(f"⚠️ faster-whisper not available: {e}")
            except Exception as e:
                logger.error(f"❌ Failed to load ASR: {e}")
        return self.whisper_model
    
    def check_llm(self):
        """Load local LLM model (Qwen 2.5B Instruct)."""
        logger.info("[2/2] Loading Qwen 2.5B Instruct...")
        
        try:
            from asr_enhancer.llm.local_llm import get_local_llm
            
            # Use Qwen 2.5B Instruct (~5GB, faster than Mistral)
            model_name = "Qwen/Qwen2.5-3B-Instruct"
            
            # Use same device as Whisper
            llm_device = self.device
            llm_compute = "float16" if self.device == "cuda" else "float32"
            
            # Load Qwen with domain classifier
            start_time = time.perf_counter()
            self.llm_model = get_local_llm(
                model_name=model_name,
                device=llm_device,
                compute_type=llm_compute,
            )
            load_time = time.perf_counter() - start_time
            
            if self.llm_model.is_available():
                self.llm_ready = True
                self.llm_provider = "local"
                self.llm_model_name = self.llm_model.model_name
                logger.info(f"✅ Local LLM loaded ({load_time:.1f}s)")
                return True
            else:
                logger.warning("⚠️ Local LLM failed to load")
                return False
                
        except ImportError as e:
            logger.warning(f"⚠️ Local LLM not available: {e}")
            logger.warning("   Install: pip install transformers torch")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Local LLM loading failed: {e}")
            return False


# Global model manager instance
models = ModelManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - loads models on startup."""
    import asyncio
    
    # Startup
    logger.info("="*50)
    logger.info("🚀 Starting ASR Enhancement Layer API")
    logger.info(f"🖥️  Device: {settings.device.upper()}")
    logger.info("="*50)
    
    # VALIDATE API KEYS (optional for local dev)
    try:
        logger.info("🔑 Validating API keys...")
        key_mgr = get_key_manager()
        if not key_mgr.check_expiration():
            logger.error("❌ API key validation failed. Server cannot start.")
            sys.exit(1)
    except RuntimeError:
        logger.warning("⚠️ API key manager not initialized - running without key validation")
        logger.warning("⚠️ This is OK for local development only!")
        key_mgr = None
    
    config = load_config()
    setup_logging(level=config.log_level)

    # Store config in app state
    app.state.config = config
    app.state.models = models
    app.state.device = settings.device
    app.state.key_manager = key_mgr

    # PRE-LOAD MODELS with configured device
    logger.info("📦 Pre-loading models for fast inference...")
    models.load_whisper(device=settings.device, compute_type=settings.compute_type)
    models.check_llm()
    
    logger.info("="*50)
    logger.info("✅ Server ready - models pre-loaded!")
    logger.info("="*50)

    # Initialize pipeline (lazy loading)
    app.state.pipeline = None
    
    # Background task to check key expiration (only if key manager exists)
    async def check_key_expiration():
        """Background task that checks key expiration every minute."""
        if key_mgr is None:
            return  # No key manager, skip expiration checks
        
        while True:
            await asyncio.sleep(60)  # Check every minute
            if not key_mgr.check_expiration():
                logger.error("❌ API KEY EXPIRED! Shutting down server...")
                os._exit(1)  # Force shutdown
    
    # Start background task
    expiration_task = asyncio.create_task(check_key_expiration())

    yield

    # Shutdown
    expiration_task.cancel()
    logger.info("Shutting down ASR Enhancement Layer API")


# Create FastAPI app
app = FastAPI(
    title="ASR Quality Enhancement Layer",
    description="""
    A production-grade post-processing pipeline for improving 
    Parakeet Multilingual ASR outputs.

    ## Features

    - **Confidence-based Error Detection**: Identifies low-confidence spans
    - **Secondary ASR Processing**: Re-transcribes problematic segments
    - **Numeric Reconstruction**: Restores missing number sequences
    - **Domain Vocabulary Correction**: Applies domain-specific terminology
    - **LLM Context Restoration**: Polishes grammar and coherence
    - **Hypothesis Fusion**: Combines multiple ASR outputs

    ## Endpoints

    - `/enhance`: Full enhancement pipeline
    - `/analyze`: Analysis only (no enhancement)
    - `/diagnostics`: Detailed diagnostics
    - `/health`: Health check
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if app.debug else "An unexpected error occurred",
        },
    )


# Include routes
app.include_router(router, prefix="/api/v1")
app.include_router(enhance_router, prefix="/api")  # Simple enhance endpoint at /api/v1/enhance


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ASR Quality Enhancement Layer",
        "version": "0.1.0",
        "device": settings.device,
        "docs": "/docs",
        "health": "/health",
    }


# Health check
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service health status and component availability.
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        components={
            "api": True,
            "device": settings.device,
            "model_loaded": models.whisper_model is not None,
            "corrector_ready": models.llm_ready,
            "pipeline": app.state.pipeline is not None,
        },
    )


def get_app() -> FastAPI:
    """Get FastAPI application instance."""
    return app


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    device: str = "cpu",
):
    """
    Run the API server.

    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload
        device: "cpu" or "cuda"/"gpu"
    """
    import uvicorn
    
    # Configure device settings BEFORE anything else
    if device in ("gpu", "cuda"):
        settings.device = "cuda"
        settings.compute_type = "float16"
    else:
        settings.device = "cpu"
        settings.compute_type = "int8"

    # Pass app object directly (not string) to preserve settings
    uvicorn.run(
        app,  # Direct reference, not string import
        host=host,
        port=port,
        reload=reload,
    )


def main():
    """CLI entry point with --cpu/--gpu flags and API key validation."""
    parser = argparse.ArgumentParser(
        description="ASR Enhancement API Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start with CPU
  python -m asr_enhancer.api.main --cpu --keys "key1,key2,key3,key4,key5,key6,key7,key8,key9,key10"
  
  # Start with GPU
  python -m asr_enhancer.api.main --gpu --keys "key1,key2,..."

Note: Exactly 10 API keys required. First key expires after 2 hours of first use.
        """
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--keys", required=True, help="API key(s) - provide at least 1 valid key (dev key expires in 2h, client keys are permanent)")
    
    # Device selection
    device_group = parser.add_mutually_exclusive_group()
    device_group.add_argument("--cpu", action="store_true", help="Force CPU usage (override GPU default)")
    device_group.add_argument("--gpu", action="store_true", help="[DEFAULT] Use GPU (CUDA) - fails if not available")
    
    args = parser.parse_args()
    
    # Parse and validate API keys
    keys = [k.strip() for k in args.keys.split(",")]
    if len(keys) < 1:
        print(f"❌ Error: Expected at least 1 API key, got {len(keys)}")
        print("   Provide at least 1 valid key with --keys")
        sys.exit(1)
    
    # Initialize key manager
    if not init_key_manager(keys):
        print("❌ Error: API key validation failed")
        print("   Check that all 10 keys are correct")
        sys.exit(1)
    
    print("✅ API keys validated")
    
    # Device selection: STRICT GPU-FIRST MODE
    import torch
    if args.cpu:
        # Explicitly requested CPU (override strict GPU mode)
        device = "cpu"
        print("🖥️  Device selected: CPU (explicitly requested with --cpu)")
    else:
        # DEFAULT: ALWAYS try to use GPU (strict mode)
        device = "cuda"
        print(f"🖥️  Device selected: CUDA (GPU strict mode)")
        
        if not torch.cuda.is_available():
            print("\n" + "="*60)
            print("❌ ERROR: GPU (CUDA) not available!")
            print("   The server is configured to run on GPU by default.")
            print("   Options:")
            print("   1. Enable GPU in your environment")
            print("   2. Use --cpu flag to run on CPU instead")
            print("="*60)
            sys.exit(1)
        
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA version: {torch.version.cuda}")
    
    run_server(host=args.host, port=args.port, reload=args.reload, device=device)


if __name__ == "__main__":
    main()
