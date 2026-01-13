from . import controller
from . import models
from importlib.metadata import version, PackageNotFoundError
from uspto_odp.models.patent_continuity import (
    ParentContinuity,
    ChildContinuity, 
    ContinuityCollection,
    ContinuityData,
)
from uspto_odp.models.patent_file_wrapper import (
    PatentFileWrapper,
    Event,
    Inventor,
    ApplicationMetadata
)

try:
    __version__ = version("uspto_odp")
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed
    __version__ = "unknown"

__all__ = [
    'controller',
    'models',
    '__version__',
    'PatentFileWrapper',
    'Event',
    'Inventor',
    'ApplicationMetadata',
    'ParentContinuity',
    'ChildContinuity',
    'ContinuityCollection',
    'ContinuityData',
]
