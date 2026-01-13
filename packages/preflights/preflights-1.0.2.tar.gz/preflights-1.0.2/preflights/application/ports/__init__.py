"""
Port interfaces for PreflightsApp.

These are the boundaries between Application and Adapters.
Application depends on these interfaces (not implementations).
"""

from preflights.application.ports.clock import ClockPort
from preflights.application.ports.config import ConfigLoaderPort
from preflights.application.ports.file_context import FileContextBuilderPort
from preflights.application.ports.filesystem import FilesystemPort
from preflights.application.ports.llm import LLMPort
from preflights.application.ports.session import SessionPort
from preflights.application.ports.uid import UIDProviderPort

__all__ = [
    "ClockPort",
    "ConfigLoaderPort",
    "FileContextBuilderPort",
    "FilesystemPort",
    "LLMPort",
    "SessionPort",
    "UIDProviderPort",
]
