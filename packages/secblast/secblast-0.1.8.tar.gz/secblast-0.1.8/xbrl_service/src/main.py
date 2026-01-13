"""
XBRL Financial Data Service

FastAPI application for parsing XBRL filings and serving financial statement data.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .config import get_settings
from .models.database import create_tables
from .api.endpoints.financials_v2 import router as financials_router


class CamelCaseJSONResponse(JSONResponse):
    """Custom JSON response that serializes Pydantic models with camelCase aliases."""

    def render(self, content: Any) -> bytes:
        if isinstance(content, BaseModel):
            # Serialize using model_dump with by_alias=True for camelCase output
            content = content.model_dump(by_alias=True, mode="json")
        return super().render(content)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting XBRL Financial Service...")
    logger.info(f"XBRL base path: {settings.xbrl_base_path}")

    # Create database tables
    await create_tables()
    logger.info("Database tables created/verified")

    yield

    # Shutdown
    logger.info("Shutting down XBRL Financial Service...")


# Create FastAPI application
app = FastAPI(
    title="SecBlast XBRL Financial Service",
    description="Parses XBRL filings and serves structured financial statement data",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=CamelCaseJSONResponse,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip compression for responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

# Include routers
app.include_router(financials_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "xbrl-financial"}


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "SecBlast XBRL Financial Service",
        "version": "1.0.0",
        "endpoints": {
            "financials": "/v2/financials",
            "balance_sheet": "/v2/financials/balance-sheet",
            "income_statement": "/v2/financials/income-statement",
            "cash_flow": "/v2/financials/cash-flow",
            "parse": "/v2/financials/parse",
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
