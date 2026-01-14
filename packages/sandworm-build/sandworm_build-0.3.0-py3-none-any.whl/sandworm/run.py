from __future__ import annotations
import collections
import collections.abc
import concurrent.futures
import enum
import graphlib
import logging
import queue
import typing

from . import core

_logger = logging.getLogger("sandworm.run")


class Result(enum.Enum):
    """Build result.

    Only `FAILURE` is falsy.

    Attributes:
        SUCCESS: Build succeeded.
        FAILURE: Build failed.
        NO_BUILD: No build was needed.
    """

    SUCCESS = enum.auto()
    FAILURE = enum.auto()
    NO_BUILD = enum.auto()

    def __bool__(self) -> bool:
        return self is not Result.FAILURE


class _Graph:
    def __init__(self) -> None:
        self.dependent_map: collections.abc.MutableMapping[core.Goal, list[core.Goal]] = (
            collections.defaultdict(list)
        )
        self.dependency_map: dict[core.Goal, set[core.Goal]] = {}
        self.leaves: set[core.Goal] = set()

    def add_goal(self, goal: core.Goal) -> None:
        self.dependency_map[goal] = (deps := set())

        if not goal.has_dependencies:
            self.leaves.add(goal)
            return

        for dependency in goal.dependencies():
            deps.add(dependency)
            self.dependent_map[dependency].append(goal)
            if dependency not in self.dependency_map:
                self.add_goal(dependency)


class _ThreadManager:
    def __init__(self, graph: _Graph, num_threads: int) -> None:
        self._graph = graph

        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)
        self._future_map: dict[core.Goal, concurrent.futures.Future[bool]] = {}
        self._done_queue: queue.SimpleQueue[core.Goal] = queue.SimpleQueue()
        self._did_build = False

    def __enter__(self) -> _ThreadManager:
        self._executor.__enter__()
        return self

    def __exit__(self, *args: typing.Any) -> None:
        for future in self._future_map.values():
            future.result()

        self._executor.__exit__(*args)

    def run(self) -> Result:
        for leaf in self._graph.leaves:
            self._submit_goal(leaf)

        while self._future_map:
            finished_goal = self._done_queue.get()
            if not self._future_map.pop(finished_goal).result():
                return Result.FAILURE
            self._mark_as_finished(finished_goal)

        return Result.SUCCESS if self._did_build else Result.NO_BUILD

    def _submit_goal(self, goal: core.Goal) -> None:
        if goal.needs_building():
            self._did_build = True
            self._future_map[goal] = self._executor.submit(self._build_goal, goal)
        else:
            _logger.debug(f"{goal.name} doesn't need to be built")
            goal.recompute_last_built()
            self._mark_as_finished(goal)

    def _build_goal(self, goal: core.Goal) -> bool:
        try:
            return goal.build()
        finally:
            self._done_queue.put(goal)

    def _mark_as_finished(self, goal: core.Goal) -> None:
        if (dependents := self._graph.dependent_map.pop(goal, None)) is None:
            return

        for dependent in dependents:
            dependencies = self._graph.dependency_map[dependent]
            dependencies.remove(goal)
            if not dependencies:
                self._graph.dependency_map.pop(dependent)
                self._submit_goal(dependent)


def build(goal: core.Goal, num_threads: int = 1) -> Result:
    """Build a goal."""
    _logger.debug(f"Goal: {goal.name}")

    graph = _Graph()
    graph.add_goal(goal)

    try:
        linearized = list(graphlib.TopologicalSorter(graph.dependency_map).static_order())
    except graphlib.CycleError as e:
        _logger.error("Dependency cycle detected:")
        for goal in e.args[1]:
            _logger.error(f"\t{goal.name}")
        return Result.FAILURE

    return _parallel_build(graph, num_threads) if num_threads > 1 else _serial_build(linearized)


def _serial_build(goals: list[core.Goal]) -> Result:
    ret = Result.NO_BUILD

    for goal in goals:
        if not goal.needs_building():
            _logger.debug(f"{goal.name} doesn't need to be built")
            continue
        ret = Result.SUCCESS

        if not goal.build():
            return Result.FAILURE

    return ret


def _parallel_build(graph: _Graph, num_threads: int) -> Result:
    with _ThreadManager(graph, num_threads) as manager:
        return manager.run()
