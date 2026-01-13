"""
FAR Search AutoGPT Plugin - Federal Acquisition Regulations search for AutoGPT.

Automatically search FAR clauses during agent execution.
"""

from far_search_autogpt.plugin import FARSearchPlugin, init_plugin

__version__ = "1.0.0"
__all__ = ["FARSearchPlugin", "init_plugin"]

