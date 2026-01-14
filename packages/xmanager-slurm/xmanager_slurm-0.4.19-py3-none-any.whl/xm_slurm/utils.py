import asyncio
import datetime as dt
import functools
import logging
import os
import pathlib
import pty
import re
import select
import shutil
import subprocess
import sys
import typing as tp

from xmanager import xm

T = tp.TypeVar("T")
P = tp.ParamSpec("P")

logger = logging.getLogger(__name__)


class CachedAwaitable(tp.Awaitable[T]):
    def __init__(self, awaitable: tp.Awaitable[T]):
        self.awaitable = awaitable
        self.result: asyncio.Future[T] | None = None

    def __await__(self):
        if not self.result:
            future = asyncio.get_event_loop().create_future()
            self.result = future
            try:
                result = yield from self.awaitable.__await__()
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)

        if not self.result.done():
            yield from self.result
        return self.result.result()


def reawaitable(f: tp.Callable[P, tp.Awaitable[T]]) -> tp.Callable[P, CachedAwaitable[T]]:
    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> CachedAwaitable[T]:
        return CachedAwaitable(f(*args, **kwargs))

    return wrapper


@functools.cache
def find_project_root() -> pathlib.Path:
    launch_script_path: pathlib.Path | None = None
    launch_script_path = pathlib.Path(sys.argv[0])

    if sys.argv[0].endswith(".py"):
        launch_script_path = pathlib.Path(sys.argv[0]).resolve()
    else:
        main_file_path = getattr(sys.modules["__main__"], "__file__", None)
        if main_file_path and os.access(main_file_path, os.R_OK):
            launch_script_path = pathlib.Path(main_file_path).resolve()

    pdir = launch_script_path.parent if launch_script_path else pathlib.Path.cwd().resolve()
    while pdir != pdir.parent:
        if (
            (pdir / "pyproject.toml").exists()
            or (pdir / "setup.py").exists()
            or (pdir / "setup.cfg").exists()
            or (pdir / "requirements.txt").exists()
            or (pdir / "requirements.in").exists()
            or (pdir / "uv.lock").exists()
            or (pdir / ".venv").exists()
        ):
            return pdir
        pdir = pdir.parent

    raise RuntimeError(f"Could not find project root from {sys.argv[0]}. Please specify `context`.")


# Cursor commands to filter out from the command data stream
_CURSOR_ESCAPE_SEQUENCES_REGEX = re.compile(
    rb"\x1b\[\?25[hl]"  # Matches cursor show/hide commands (CSI ?25h and CSI ?25l)
    rb"|\x1b\[[0-9;]*[Hf]"  # Matches cursor position commands (CSI n;mH and CSI n;mf)
    rb"|\x1b\[s"  # Matches cursor save position (CSI s)
    rb"|\x1b\[u"  # Matches cursor restore position (CSI u)
    rb"|\x1b\[2J"  # Matches clear screen (CSI 2J)
    rb"|\x1b\[K"  # Matches clear line (CSI K)
)


def run_command(
    args: tp.Sequence[str] | xm.SequentialArgs,
    env: dict[str, str] | None = None,
    tty: bool = False,
    cwd: str | os.PathLike[str] | None = None,
    stdin: tp.IO[tp.AnyStr] | str | None = None,
    check: bool = False,
    return_stdout: bool = False,
    return_stderr: bool = False,
) -> subprocess.CompletedProcess[str]:
    if isinstance(args, xm.SequentialArgs):
        args = args.to_list()
    args = list(args)

    executable = shutil.which(args[0])
    if not executable:
        raise RuntimeError(f"Couldn't find executable {args[0]}")
    executable = pathlib.Path(executable)

    subprocess_env = os.environ.copy() | (env if env else {})
    if executable.name == "docker" and args[1] == "buildx":
        subprocess_env |= {"DOCKER_CLI_EXPERIMENTAL": "enabled"}

    logger.debug(f"command: {' '.join(args)}")

    stdout_master, stdout_slave = pty.openpty()
    stderr_master, stderr_slave = pty.openpty()

    stdout_data, stderr_data = b"", b""
    with subprocess.Popen(
        executable=executable,
        args=args,
        shell=False,
        text=True,
        bufsize=0,
        stdin=subprocess.PIPE if stdin else None,
        stdout=stdout_slave,
        stderr=stderr_slave,
        start_new_session=True,
        close_fds=True,
        cwd=cwd,
        env=subprocess_env,
    ) as process:
        os.close(stdout_slave)
        os.close(stderr_slave)

        if stdin and process.stdin:
            process.stdin.write(stdin if isinstance(stdin, str) else tp.cast(str, stdin.read()))
            process.stdin.close()

        fds = [stdout_master, stderr_master]
        while fds:
            rlist, _, _ = select.select(fds, [], [])
            for fd in rlist:
                try:
                    data = os.read(fd, 1024)
                except OSError:
                    data = None

                if not data:
                    os.close(fd)
                    fds.remove(fd)
                    continue

                data = _CURSOR_ESCAPE_SEQUENCES_REGEX.sub(b"", data)

                if fd == stdout_master:
                    if return_stdout:
                        stdout_data += data
                    if tty:
                        os.write(pty.STDOUT_FILENO, data)
                elif fd == stderr_master:
                    if return_stderr:
                        stderr_data += data
                    if tty:
                        os.write(pty.STDERR_FILENO, data)
                else:
                    raise RuntimeError("Unexpected file descriptor")

    stdout = stdout_data.decode(errors="replace") if stdout_data else ""
    stderr = stderr_data.decode(errors="replace") if stderr_data else ""

    logger.debug(f"return code: {process.returncode}")
    if stdout:
        logger.debug(f"stdout: {stdout}")
    if stderr:
        logger.debug(f"stderr: {stderr}")

    retcode = process.poll()
    assert retcode is not None

    if check and retcode:
        raise subprocess.CalledProcessError(retcode, process.args)
    return subprocess.CompletedProcess(
        process.args,
        retcode,
        stdout=stdout,
        stderr=stderr,
    )


def timestr_from_timedelta(time: dt.timedelta) -> str:
    days = time.days
    hours, remainder = divmod(time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}-{hours:02}:{minutes:02}:{seconds:02}"
