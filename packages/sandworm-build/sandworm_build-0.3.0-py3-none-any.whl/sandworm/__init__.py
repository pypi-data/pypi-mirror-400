import logging

from . import cli
from . import helpers
from .cli import VERSION
from .core import (
    AlwaysGoal,
    Builder,
    Cleaner,
    Context,
    ContextNotSetError,
    DuplicateNameError,
    Error,
    FileGoal,
    Goal,
    GOAL_NAME_PATTERN,
    ThinGoal,
)
from .run import build, Result

logger = logging.getLogger("sandworm")

SUCCESS = Result.SUCCESS
FAILURE = Result.FAILURE
NO_ACTION = Result.NO_BUILD

__all__ = (
    "AlwaysGoal",
    "Builder",
    "Cleaner",
    "build",
    "Context",
    "ContextNotSetError",
    "cli",
    "DuplicateNameError",
    "Error",
    "FAILURE",
    "FileGoal",
    "Goal",
    "GOAL_NAME_PATTERN",
    "helpers",
    "logger",
    "NO_ACTION",
    "Result",
    "SUCCESS",
    "ThinGoal",
    "VERSION",
)
