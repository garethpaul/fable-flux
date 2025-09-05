"""
Story Generation System
A comprehensive system for generating educational children's stories using AI
"""

from .story_generator import StoryGenerator
from .diversity_tracker import DiversityTracker
from .poe_client import PoeClient
from .story_validator import StoryValidator
from .batch_processor import BatchProcessor

__version__ = "1.0.0"
__author__ = "Story Generation Team"

# Convenience imports for easy access
__all__ = [
    "StoryGenerator",
    "DiversityTracker", 
    "PoeClient",
    "StoryValidator",
    "BatchProcessor"
]