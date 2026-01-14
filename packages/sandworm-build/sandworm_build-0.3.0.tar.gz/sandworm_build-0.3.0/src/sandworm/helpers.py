import functools
import logging
import pathlib
import shutil
import subprocess
import tempfile

_logger = logging.getLogger("sandworm.helpers")


def run_command(cmd: str) -> int:
    """Run a shell command.

    The stdout/stderr are printed to our stdout.

    Arguments:
        cmd (str): Shell command.

    Returns:
        int: Exit code of the command.
    """
    _logger.debug(f"Running shell command: {cmd}")
    with tempfile.TemporaryFile("w+") as f:
        p = subprocess.run(cmd, shell=True, text=True, stdout=f, stderr=f)
        f.seek(0)
        output = f.read()
    print(output, end="")
    if output and not output.endswith("\n"):
        print("")
    return p.returncode


@functools.lru_cache(1)
def c_defaults() -> dict[str, pathlib.Path]:
    """Resolve the paths to common binaries used for C/C++ compilation.

    Returns:
        dict[str, pathlib.Path]: The keys will be a subset (possibly non-proper) of CC, CXX, LD, AR, and AS.
    """
    requirements = (
        ("CC", ("cc", "gcc", "clang")),
        ("CXX", ("c++", "g++", "clang++")),
        ("LD", ("ld",)),
        ("AR", ("ar",)),
        ("AS", ("as",)),
    )
    defaults = {}
    for var, cmds in requirements:
        for cmd in cmds:
            if (result := shutil.which(cmd)) is not None:
                _logger.debug(f"{var} resolved to {result}")
                defaults[var] = pathlib.Path(result)
                break
    return defaults
