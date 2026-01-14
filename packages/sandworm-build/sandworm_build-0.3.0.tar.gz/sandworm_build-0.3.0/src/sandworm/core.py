from __future__ import annotations
import abc
import collections.abc
import datetime
import importlib.util
import logging
import os
import pathlib
import re
import typing

import dotenv

_logger = logging.getLogger("sandworm.core")

Builder = collections.abc.Callable[["Goal"], bool]
Cleaner = collections.abc.Callable[["Context"], bool]

GOAL_NAME_PATTERN = re.compile(r"\S+$")

_sentinel = object()


class Error(Exception):
    pass


class ContextNotSetError(Error):
    pass


class DuplicateNameError(Error):
    pass


class Goal(abc.ABC):
    """Goal to be built."""

    def __init__(self, name: str, builder: Builder | None = None) -> None:
        """
        Arguments:
            name (str): Name of the goal.
            builder (Builder | None): Function to build the goal.

        Raises:
            ValueError: An invalid name was provided.  Names must be non-empty and not contain whitespace.
        """
        if not GOAL_NAME_PATTERN.match(name):
            raise ValueError(f'Invalid name: "{name}"')

        self._name = name
        self._builder = builder

        self._dirty = False
        self._ctx: Context | None = None
        self._dependencies: list[Goal] = []
        self._build_time: datetime.datetime | None = None
        self._build_time_calculated = False

    @typing.final
    def __eq__(self, other: object) -> bool:
        return self is other

    @typing.final
    def __hash__(self) -> int:
        return id(self)

    @property
    def name(self) -> str:
        return self._name

    @typing.final
    @property
    def context(self) -> Context:
        if self._ctx is None:
            raise ContextNotSetError
        return self._ctx

    @typing.final
    def dependencies(self) -> collections.abc.Iterator[Goal]:
        """Iterate over the dependencies."""
        yield from self._dependencies

    @typing.final
    def add_dependency(self, dependency: Goal) -> None:
        """Add a dependency."""
        if self._ctx is not None:
            dependency._set_context_if_unset(self._ctx)
        self._dependencies.append(dependency)

    @typing.final
    @property
    def has_dependencies(self) -> bool:
        return bool(self._dependencies)

    @abc.abstractmethod
    def exists(self) -> bool:
        """Does the goal exist?"""
        raise NotImplementedError

    def last_built(self) -> datetime.datetime | None:
        """Determine the last time the goal was built.

        Returns:
            datetime.datetime: Timestamp or `None` if the goal doesn't exist or if a build time doesn't make
            sense.
        """
        return None

    @typing.final
    def recompute_last_built(self) -> datetime.datetime | None:
        """Force the last build time to be recomputed and saved."""
        self._build_time = self.last_built()
        self._build_time_calculated = True
        return self._build_time

    @typing.final
    def needs_building(self) -> bool:
        """Does the goal need to be built?"""
        if not self.exists():
            _logger.debug(f"{self.name} needs to be built because it does not exist")
            return True

        last_built = self._get_last_built()
        for dependency in self._dependencies:
            if dependency._dirty:
                _logger.debug(f"{self.name} needs to be built because dependency {dependency.name} is dirty")
                return True

            if (
                last_built is not None
                and (dep_last_built := dependency._get_last_built()) is not None
                and dep_last_built > last_built
            ):
                _logger.debug(f"{self.name} needs to be built because dependency {dependency.name} is newer")
                return True

        return False

    @typing.final
    def build(self) -> bool:
        """Build the goal.

        This method should not be called by the user directly.  Instead, `sandworm.build(goal)` should be
        used.

        Returns:
            bool: Was the build successful?
        """
        if self._builder:
            _logger.info(f"Building {self.name}")
            try:
                if not self._builder(self):
                    _logger.error(f"Failed to build {self.name}")
                    return False
            except Exception:
                _logger.exception(f"Error encountered while building {self.name}")
                return False
            _logger.debug(f"{self.name} built successfully")
        elif not self.exists():
            _logger.error(f"No logic exists to build {self.name}")
            return False

        self._dirty = True
        self.recompute_last_built()
        return True

    def _set_context_if_unset(self, ctx: Context) -> None:
        if self._ctx is None:
            self._ctx = ctx
        for dependency in self._dependencies:
            dependency._set_context_if_unset(ctx)

    def _get_last_built(self) -> datetime.datetime | None:
        return self._build_time if self._build_time_calculated else self.recompute_last_built()


class FileGoal(Goal):
    """Represents a file to be created."""

    def __init__(self, path: pathlib.Path, builder: Builder | None = None) -> None:
        super().__init__(str(path), builder)
        self._path = path

    @property
    def path(self) -> pathlib.Path:
        return self._path

    def exists(self) -> bool:
        return self._path.exists()

    def last_built(self) -> datetime.datetime | None:
        return datetime.datetime.fromtimestamp(self._path.stat().st_mtime) if self._path.exists() else None


class ThinGoal(Goal):
    """Goal that always registers as existing.

    This is meant merely to be a wrapper around its dependencies as it is only built if one or more of its
    dependencies are dirty.
    """

    def exists(self) -> bool:
        return True

    def last_built(self) -> datetime.datetime | None:
        winner: datetime.datetime | None = None
        for dep in self.dependencies():
            if (build_time := dep._get_last_built()) is not None and (winner is None or build_time > winner):
                winner = build_time
        return winner


class AlwaysGoal(Goal):
    """Goal that never registers as existing and so is always built."""

    def exists(self) -> bool:
        return False


@typing.final
class Context:
    """Build context."""

    def __init__(
        self, directory: pathlib.Path, *, parent: Context | None = None, use_env: bool = True
    ) -> None:
        if not directory.is_dir():
            raise NotADirectoryError(directory)

        self._basedir = directory.resolve()
        self._parent = parent
        self._use_env = use_env

        self._children: list[Context] = []
        self._main_goal: Goal | None = None
        self._variables: dict[str, typing.Any] = {}
        self._blocked_variables: set[str] = set()
        self._goals: dict[str, Goal] = {}
        self._cleaners: list[Cleaner] = []

        if parent is not None:
            parent._children.insert(0, self)

    @classmethod
    def from_directory(
        cls, directory: pathlib.Path, *, parent: Context | None = None, use_env: bool = True
    ) -> Context:
        """Create a context by loading a Wormfile.

        Arguments:
            directory (pathlib.Path): Directory containing Wormfile.py.
            parent (sandworm.Context | None): Optional parent from which the new context will inherit.
            use_env (bool): Should environment variables be used by the context?  This value is effectively
            ignored if `parent` is provided.

        Returns:
            sandworm.Context

        Raises:
            ImportError: The Wormfile couldn't be loaded.
        """
        if not use_env and parent is not None:
            _logger.warning("use_env=False will be ignored becase a parent context is provided")

        wormfile = directory / "Wormfile.py"
        _logger.debug(f"Loading {wormfile}")

        spec = importlib.util.spec_from_file_location("Wormfile", wormfile)
        if spec is None:
            raise ImportError(str(wormfile))
        module = importlib.util.module_from_spec(spec)
        if spec.loader is None:
            raise ImportError(str(wormfile))
        spec.loader.exec_module(module)

        ctx = Context(directory, parent=parent, use_env=use_env)

        if (config_file := directory / "sandworm.env").is_file():
            _logger.debug(f"Loading configuration from {config_file}")
            for key, value in dotenv.dotenv_values(config_file).items():
                ctx[key] = value or ""

        module.add_goals(ctx)
        return ctx

    @property
    def basedir(self) -> pathlib.Path:
        return self._basedir

    @property
    def main_goal(self) -> Goal | None:
        return self._main_goal

    def create_child(self) -> Context:
        """Create a child context with the same base directory."""
        return Context(self._basedir, parent=self)

    def add_goal(self, goal: Goal, *, name: str | None = None, main: bool = False) -> None:
        """Add a goal to be managed by this context.

        Arguments:
            goal (sandworm.Goal): Goal to be added.
            name (str | None): Name to reference the goal by.  If `None`, then the goal's own name will be
            used.
            main (bool): Is this to be the context's main goal?

        Raises:
            ValueError: An invalid name was provided.
            sandworm.DuplicateNameError: A duplicate name was provided.
        """
        if name is None:
            name = goal.name
        elif not GOAL_NAME_PATTERN.match(name):
            raise ValueError(f'Invalid name: "{name}"')

        if name in self._goals:
            raise DuplicateNameError(name)

        goal._set_context_if_unset(self)
        self._goals[name] = goal
        if main:
            self._main_goal = goal

    def lookup_goal(self, name: str) -> Goal | None:
        """Look up a registered goal by name."""
        return self._goals.get(name)

    def goals(self) -> collections.abc.Iterator[tuple[str, Goal]]:
        """Iterate over the registered goals.

        Returns:
            Iterator[tuple[str, sandworm.Goal]]: Iterator of names and goals.
        """
        yield from self._goals.items()

    def add_cleaner(self, cleaner: Cleaner) -> None:
        """Add a cleaner."""
        self._cleaners.insert(0, cleaner)

    def clean(self) -> bool:
        """Run all of the registered cleaners.

        All child contexts will be cleaned first (in the reverse order that they were added).  For each
        context, the cleaners will be called in the reverse order that they were added.

        Returns:
            bool: Were all of the cleaners successful?
        """
        return all(map(Context.clean, self._children)) and all(cleaner(self) for cleaner in self._cleaners)

    def get(self, key: str, default: typing.Any = None) -> typing.Any:
        """Look up a variable safely.

        First, this context is searched.  If the variable is not found, then the parent is searched (if there
        is one) and so on.  At the end, if the variable is still not found, the environment is searched
        (unless `use_env` was `False`).

        Arguments:
            key (str): Name of the variable.
            default (Any): Value to return if the key isn't found.

        Returns:
            Any: The value of the variable if it was found and the default otherwise.
        """
        if key in self._blocked_variables:
            return default

        if (value := self._variables.get(key, _sentinel)) is not _sentinel:
            return value

        if self._parent is not None:
            return self._parent.get(key, default)

        if self._use_env:
            return os.environ.get(key, default)

        return default

    def __contains__(self, key: str) -> bool:
        """Like `get`, the ancestry and environment are included in the search."""
        return self.get(key, _sentinel) is not _sentinel

    def __getitem__(self, key: str) -> typing.Any:
        """Like `get`, the ancestry and environment are included in the search."""
        if (value := self.get(key, _sentinel)) is _sentinel:
            raise KeyError(key)
        return value

    def __delitem__(self, key: str) -> None:
        self.pop(key)

    def __setitem__(self, key: str, value: typing.Any) -> None:
        self._blocked_variables.discard(key)
        self._variables[key] = value

    def pop(self, key: str, default: typing.Any = _sentinel) -> typing.Any:
        """Pop a variable.

        In the case that the variable is actually set in an ancestor context or the environment, the variable
        will technically remain but this context will be blocked from accessing it and thus it will appear,
        from this context and any child's perspective, that the variable has been removed.
        """
        if (value := self.get(key, _sentinel)) is _sentinel:
            if default is _sentinel:
                raise KeyError(key)
            return default

        self._variables.pop(key, None)
        self._blocked_variables.add(key)
        return value

    def setdefault(self, key: str, value: typing.Any) -> typing.Any:
        """Set a variable only if it hasn't already been set.

        Like `get`, the ancestry and environment are included in the search.

        Returns:
            Any: Actual value of the variable.
        """
        if (current_value := self.get(key, _sentinel)) is _sentinel:
            self[key] = value
            current_value = value
        return current_value

    def variables(self) -> dict[str, typing.Any]:
        """Provides a copy of the variables.

        Like `get`, the ancestry and environment are included.
        """
        if self._parent is not None:
            variables = self._parent.variables()
        elif self._use_env:
            variables = os.environ.copy()
        else:
            variables = {}
        variables.update(self._variables)
        return variables
