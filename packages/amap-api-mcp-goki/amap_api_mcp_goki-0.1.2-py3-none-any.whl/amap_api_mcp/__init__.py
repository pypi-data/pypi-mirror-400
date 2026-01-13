"""Amap API MCP Server.

A Model Context Protocol (MCP) server for integrating with Amap (高德地图) API,
providing weather information and other location-based services.
"""

from .server import main

__version__ = "0.1.0"
__all__ = ["main"]