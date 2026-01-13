"""
Orca App Factory
================

Factory functions for creating FastAPI applications with standard Orca configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import os
from ..config import VERSION

def create_orca_app(
    title: str = "Orca AI Agent",
    version: str = None,
    description: str = "AI agent with Orca platform integration",
    debug: bool = False
) -> FastAPI:
    """
    Create a FastAPI application with standard Orca configuration.
    
    Args:
        title: Application title
        version: Application version (defaults to ORCA_APP_VERSION or APP_VERSION env var, then SDK version)
        description: Application description
        debug: Enable debug mode
        
    Returns:
        Configured FastAPI application
    """
    
    # Resolve version
    if version is None:
        version = os.getenv("ORCA_APP_VERSION") or os.getenv("APP_VERSION") or VERSION
    
    # Create the app
    app = FastAPI(
        title=title,
        version=version,
        description=description,
        debug=debug,
        docs_url="/docs" if debug else None,
        redoc_url="/redoc" if debug else None
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure as needed for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for production
    if not debug:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure as needed for production
        )
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    return app
