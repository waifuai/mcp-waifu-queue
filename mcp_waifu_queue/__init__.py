"""
MCP Waifu Queue Package.

This package implements an MCP (Model Context Protocol) server for conversational AI
text generation using Redis queues for asynchronous processing. The system supports
multiple AI providers (OpenRouter and Google Gemini) with automatic fallback and
configurable provider selection.

The package provides:
- MCP server implementation with FastMCP
- Redis-based job queue system using RQ (Redis Queue)
- Multi-provider AI text generation (OpenRouter/Gemini)
- Configuration management via Pydantic settings
- Async request processing with job status tracking

Main components:
- main.py: MCP server entry point and tool/resource definitions
- config.py: Configuration management
- respond.py: Provider dispatch and text generation logic
- task_queue.py: Redis queue management
- worker.py: RQ worker process
- models.py: Pydantic models for requests/responses
- utils.py: Utility functions for the worker
- providers/: Provider-specific implementations

Version: 0.1.0
"""
# This file makes the directory a Python package. It can be empty.
__version__ = "0.1.0"