# coding: utf-8

__version__ = "1.2.2"

# Make Sandbox available at package level
from .sandbox import Sandbox, AsyncSandbox

__all__ = ["Sandbox", "AsyncSandbox"]
