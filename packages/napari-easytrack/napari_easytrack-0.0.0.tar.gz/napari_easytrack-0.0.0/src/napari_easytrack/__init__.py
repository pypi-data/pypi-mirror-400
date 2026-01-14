"""napari_easytrack - Cell tracking with btrack presets and optimization."""

__version__ = "0.1.1"

from .widgets.widget import BtrackPresetWidget
from .widgets.optim_widget import BtrackOptimizationWidget

__all__ = [
    "BtrackPresetWidget",
    "BtrackOptimizationWidget",
]