"""
Dance Information Retrieval (DanceIR) Toolbox

A modular toolbox for dance motion analysis, feature extraction, and tempo estimation.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("danceir")
except PackageNotFoundError:
    __version__ = "0.0.0"

# Config module
from . import config

# Preprocessing module
from . import preprocessing

# I/O module
from . import io

# Features module
from . import features

# Analysis module
from . import analysis

# Pipelines module (high-level workflows)
from . import pipelines

# Evaluation module
from . import evaluation

__all__ = [
    "config",
    "preprocessing",
    "io",
    "features",
    "analysis",
    "pipelines",
    "evaluation",
]

