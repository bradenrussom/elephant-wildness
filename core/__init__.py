# core/__init__.py
"""Core utilities for MVP Standards Checker"""

from .document_processor import DocumentProcessor
from .text_analyzer import TextAnalyzer
from .utils import load_config, get_module_config

__all__ = ['DocumentProcessor', 'TextAnalyzer', 'load_config', 'get_module_config']
