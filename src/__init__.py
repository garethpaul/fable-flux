"""
Story Generation System
A comprehensive system for generating educational children's stories using AI
"""

from importlib import import_module

__version__ = "1.0.0"
__author__ = "Story Generation Team"

__all__ = [
    "StoryGenerator",
    "DiversityTracker",
    "PoeClient",
    "StoryValidator",
    "BatchProcessor",
]

_EXPORT_MODULES = {
    "StoryGenerator": ".story_generator",
    "DiversityTracker": ".diversity_tracker",
    "PoeClient": ".poe_client",
    "StoryValidator": ".story_validator",
    "BatchProcessor": ".batch_processor",
}


def __getattr__(name):
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError("module 'src' has no attribute {!r}".format(name))

    value = getattr(import_module(module_name, __name__), name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(__all__))
