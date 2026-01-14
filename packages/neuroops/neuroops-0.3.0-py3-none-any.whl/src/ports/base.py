from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, List, Union
import numpy as np

class NeuroSource(ABC):
    """
    Port (Interface) for all data sources.
    Defines the contract that must be fulfilled by any Adapter (Local or Cloud).
    """

    @abstractmethod
    def get_meta(self) -> Dict[str, Any]:
        """
        Returns metadata about the dataset.
        Must include: 'shape' (tuple), 'affine' (array-like, if MRI), 'sfreq' (float, if EEG).
        """
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for this source (e.g., filename or URI)."""
        pass

    # --- DOMAIN SPECIFIC METHODS ---

    def get_slice(self, axis: int, index: int) -> np.ndarray:
        """
        Fetches a 2D slice for MRI.
        Should raise NotImplementedError if not MRI.
        """
        raise NotImplementedError("This source does not support Volumetric Slicing.")

    def get_signal(self, start_time: float, end_time: float, channels: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fetches time-series data for EEG.
        Returns: (data, times)
        Should raise NotImplementedError if not EEG.
        """
        raise NotImplementedError("This source does not support Time-Series fetching.")
