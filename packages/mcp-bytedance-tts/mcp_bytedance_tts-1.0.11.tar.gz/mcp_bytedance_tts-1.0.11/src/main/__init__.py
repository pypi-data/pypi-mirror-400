"""
MCP Bytedance TTS - A Model Context Protocol server for text-to-speech conversion.

Uses Bytedance OpenSpeech TTS API to generate audio from text.
"""

import asyncio
from .server import run_server

__version__ = "1.0.0"

def main():
    """Entry point for the MCP server."""
    asyncio.run(run_server())

__all__ = ["main", "__version__"]
