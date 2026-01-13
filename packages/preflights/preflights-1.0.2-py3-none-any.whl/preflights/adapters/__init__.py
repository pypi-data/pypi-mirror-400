"""
Preflights Adapters.

Mock/Fake implementations for testing and development.
Production adapters will be in separate modules.
"""

from preflights.adapters.default_config import DefaultConfigLoader
from preflights.adapters.fake_filesystem import FakeFilesystemAdapter
from preflights.adapters.fixed_clock import FixedClockProvider
from preflights.adapters.in_memory_session import InMemorySessionAdapter
from preflights.adapters.mock_llm import MockLLMAdapter
from preflights.adapters.sequential_uid import SequentialUIDProvider
from preflights.adapters.simple_file_context import SimpleFileContextBuilder

__all__ = [
    "DefaultConfigLoader",
    "FakeFilesystemAdapter",
    "FixedClockProvider",
    "InMemorySessionAdapter",
    "MockLLMAdapter",
    "SequentialUIDProvider",
    "SimpleFileContextBuilder",
]
