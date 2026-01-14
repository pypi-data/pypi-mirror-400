"""
NeuroOps Integrations Package

Plugins for seamless integration with popular neuroscience tools.
"""

from .mne_plugin import (
    compare_preprocessing,
    compare_ica,
    compare_filter,
    compare  # Alias
)

__all__ = [
    'compare_preprocessing',
    'compare_ica',
    'compare_filter',
    'compare'
]
