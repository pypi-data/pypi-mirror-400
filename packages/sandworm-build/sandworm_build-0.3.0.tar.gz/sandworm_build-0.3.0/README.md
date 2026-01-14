Sandworm is a minimalistic build tool inspired by Make.

# Getting started

Instead of a Makefile, you create a Wormfile.py.  A template can be created by

```sh
sandworm init
```

If you look at the generated file, you'll see this function:

```python
def add_goals(ctx: sandworm.Context) -> None:
    pass
```

This is where you define and add your goals (akin to Make's targets).

# Goals

`sandworm.Goal` is an abstract base class which represents some goal to be achieved/built (e.g., a binary, a Docker image).

You must implement the `exists` method:

```python
    def exists(self) -> bool:
        ...
```

As the name suggests, this is how Sandworm knows if the goal already exists.

You may also define

```python
    def last_built(self) -> datetime.datetime | None:
        ...
```

This returns when the goal was last built or `None` if either the goal doesn't exist or if a build time doesn't make sense for the goal.  The default implementation returns `None`.

In your subclass, you must call the base class' `__init__` method:

```python
    def __init__(self, name: str, builder: Callable[[Goal], bool] | None = None) -> None:
        ...
```

`name` is how the goal will be described in log messages.  It must be non-empty and not contain any whitespace.  `builder`, if specified, is a function that will be called if the goal needs to be built.  The return value indicates whether or not the build was successful.  There are situations when you would want to have no builder (see [`ThinGoal`](#thingoal)).

Goals can also depend upon other goals:

```python
goal.add_dependency(other_goal)
```

Once you've set up your goals, you can add them to the build context:

```python
ctx.add_goal(goal)
```

Note that you don't have to add dependencies to the context (though you can).  The idea is that you should only add goals which you want to be able to build from your command line.  For example, if you had a goal with the name "libfoo.so", then you could add it to your context and run

```sh
sandworm build libfoo.so
```

You wouldn't need to add, say, foo.o unless you wanted to be able to build that by itself from the command line.

You can alternatively choose a different name to expose to the command line:

```python
ctx.add_goal(goal, name="library")
```

That way, you can do

```sh
sandworm build library
```

You can set a goal to be the context's main goal by

```python
ctx.add_goal(goal, main=True)
```

That way, you can omit the name:

```sh
sandworm build
```

## Parallel builds

You can also perform parallel builds by setting the number of threads to use:

```sh
sandworm build [GOAL] -n 5
```

If you specify a negative number of threads, then Sandworm will use however many CPU cores you have.

## When goals are built

When you run `sandworm build [GOAL]`, the dependency graph is linearized and the goals are checked one by one, starting with the bottom-most dependencies.

If a goal doesn't exist, then it needs to be built.  If such a goal doesn't have a builder, then the build will fail.

If any of a goal's dependencies needed to be built, then it needs to be built.

If `last_built` returns non-`None` and any of the dependencies has a newer (which also means non-`None`) last build time, then it needs to be built.

## Goal subclasses

Several `Goal` subclasses are provided.

### FileGoal

`FileGoal` represents a file to be built.  It has a read-only `path` attribute which is a `pathlib.Path`.

```python
goal = sandworm.FileGoal(pathlib.Path("path/to/file"))
```

### ThinGoal

For `ThinGoal`, `exists` always returns `True`.  Its intended use case is as an aggregation of other goals.

```python
goal = sandworm.ThinGoal("Goal")
```

### AlwaysGoal

`AlwaysGoal` is the opposite of `ThinGoal` in that `exists` always returns `False`.  Therefore, the goal will always be built.

```python
goal = sandworm.AlwaysGoal("Goal", builder)
```

# Context

By the time your builder function is called, the context will be available to you via the goal:

```python
def builder(goal: sandworm.Goal) -> bool:
    ctx = goal.context
    ...
```

The context has a read-only `basedir` attribute which is a `pathlib.Path` giving the directory containing the Wormfile which set up the context.

## Variables

Contexts can also be used to supply variables during build time:

```python
ctx["foo"] = "bar"
assert "foo" in ctx
assert ctx.setdefault("foo", "baz") == "bar"
```

The values can be of any type.

One variable placed in the top-most context is "SANDWORM_BUILD_TARGET".  Its value is the name that was passed to `sandworm build` (or an empty string if no name was provided).  For example, if you had

```python
goal = sandworm.FileGoal(pathlib.Path("path/to/libfoo.so"), builder)
ctx.add_goal(goal, name="library")
```

and ran

```sh
sandworm build library
```

then `ctx["SANDWORM_BUILD_TARGET"]` would be "library".

Note that the variable will only be added to the context after all of the Wormfiles have been loaded.

## Recursive Sandworm considered safe

Sandworm allows for recursive use.  That is, from one Wormfile you can load another:

```python
directory = pathlib.Path("path/to/other/Wormfile.py").parent
child_ctx = sandworm.Context.from_directory(directory, parent=ctx)
```

This loads the Wormfile.py in that folder, creates a context, and passes the context to the Wormfile's `add_goals` function.

By setting `parent` equal to your current context, you allow the child context to inherit your variables.  Variable lookup is as follows: When you run `ctx["foo"]` or `ctx.get("foo")`, it will first check if "foo" has been set for the context.  If not, then the parent context will be checked if there is one.  If variable still isn't found, then that context's parent will be checked and so on.  Finally, if the variable hasn't been set anywhere in the context's ancestry, then the environment variables will be checked.  If you want to disable the use of environment variables, run Sandworm with "--no-env":

```sh
sandworm --no-env build
```

You can create a child context directly without loading a Wormfile:

```python
child_ctx = ctx.create_child()
```

This can be useful if you want different goals to see different variables.

When you run `sandworm build GOAL`, only the top-most context is checked.  If you want to expose a goal from a child context, it must be explicitly added to the parent:

```python
goal = child_ctx.lookup_goal("GOAL")
assert goal is not None
ctx.add_goal(goal, name="GOAL")
```

## Removing variables

Variables can be from a context via `pop` and `__delitem__`.  In the case that the variable actually comes from an ancestor context or the environment, the variable will not actually be removed.  Instead, the context will be blocked from accessing it and so it will appear as it has been removed:

```python
ctx["foo"] = "bar"
child_ctx = ctx.create_child()
assert child_ctx["foo"] == "bar"
assert "foo" not in child_ctx
assert ctx["foo"] == "bar"
```

# Cleaning

You can register cleanup functions:

```python
def cleaner(ctx: sandworm.Context) -> bool:
    ...

ctx.add_cleaner(cleaner)
```

When you run `sandworm clean`, the cleaners will be called in the reverse order that they were added.  Furthermore, before a context's cleaners are called, all child contexts' cleaners are called.  For example, suppose Context 1 has two children, Context 2 and Context 3.  Context 3 has a child, Context 4.  Assuming that Context 2 was created before Context 3, Context 4's cleaners will be called first (in reverse order), then Context 3, then Context 2, and finally Context 1.

If any of the cleaners returns `False`, then no more cleaners will be run.

# List goals

You can list the goals exposed by the context by

```sh
sandworm list
```

If there is a main goal, then its name will be prefixed with "* ".

# Configuration files

If you place a sandworm.env file in the same directory as your Wormfile, it will get treated like a dotenv file.  The variables contained therein won't be added to the environment but instead will be set in the context before `add_goals` is called.  Variables without values will be set to the empty string.

# Helpers

The submodule `sandworm.helpers` provides some helper functions.

`sandworm.helpers.run_command` runs a shell command and returns the exit code:

```python
assert sandworm.helpers.run_command("echo foo") == 0
```

It prints the stdout/stderr to our stdout.

`sandworm.helpers.c_defaults` attempts to resolve common binary paths for building C/C++ programs.  It returns a dictionary that might look like

```python
{
    "CC": PosixPath("/usr/bin/cc"),
    "CXX": PosixPath("/usr/bin/c++"),
    "LD": PosixPath("/usr/bin/ld"),
    "AR": PosixPath("/usr/bin/ar"),
    "AS": PosixPath("/usr/bin/as")
}
```

# Logging

Sandworm's logger is available via `sandworm.logger`.  By default, the logging format is `"%(message)s"`.  However, you can change this via the `SANDWORM_LOG_FORMAT` environment variable.