import asyncio
import collections.abc
import dataclasses
import functools
import getpass
import hashlib
import importlib
import importlib.resources
import logging
import operator
import os
import pathlib
import re
import shlex
import shutil
import subprocess
import sys
import typing as tp

import asyncssh
import backoff
import jinja2 as j2
import more_itertools as mit
from asyncssh.auth import KbdIntPrompts, KbdIntResponse
from asyncssh.misc import MaybeAwait
from rich.console import ConsoleRenderable
from rich.rule import Rule
from rich.text import Text
from xmanager import xm

from xm_slurm import (
    batching,
    config,
    constants,
    dependencies,
    executors,
    filesystems,
    job_blocks,
    status,
    utils,
)
from xm_slurm.console import console
from xm_slurm.types import Descriptor

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 30.0
_BATCHED_BATCH_SIZE = 16
_BATCHED_TIMEOUT = 0.2


class SlurmExecutionError(Exception): ...


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmJob:
    job_id: str

    @property
    def is_array_job(self) -> bool:
        return isinstance(self, SlurmArrayJob)

    @property
    def is_heterogeneous_job(self) -> bool:
        return isinstance(self, SlurmHeterogeneousJob)

    def __hash__(self) -> int:
        return hash((type(self), self.job_id))


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmArrayJob(SlurmJob):
    array_job_id: str
    array_task_id: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmHeterogeneousJob(SlurmJob):
    het_job_id: str
    het_component_id: str


SlurmJobT = tp.TypeVar("SlurmJobT", bound=SlurmJob, covariant=True)


class SlurmJobDescriptor(Descriptor[SlurmJobT, str]):
    def __set_name__(self, owner: type, name: str):
        del owner
        self.job = f"_{name}"

    def __get__(self, instance: object | None, owner: tp.Type[object] | None = None) -> SlurmJobT:
        del owner
        return getattr(instance, self.job)

    def __set__(self, instance: object, value: str):
        _setattr = object.__setattr__ if not hasattr(instance, self.job) else setattr

        match = constants.SLURM_JOB_ID_REGEX.match(value)
        if match is None:
            raise ValueError(f"Invalid Slurm job ID: {value}")
        groups = match.groupdict()

        job_id = groups["jobid"]
        if array_task_id := groups.get("arraytaskid"):
            _setattr(
                instance,
                self.job,
                SlurmArrayJob(job_id=value, array_job_id=job_id, array_task_id=array_task_id),
            )
        elif het_component_id := groups.get("componentid"):
            _setattr(
                instance,
                self.job,
                SlurmHeterogeneousJob(
                    job_id=value, het_job_id=job_id, het_component_id=het_component_id
                ),
            )
        else:
            _setattr(instance, self.job, SlurmJob(job_id=value))


def _group_by_ssh_configs(
    ssh_configs: tp.Sequence[config.SSHConfig], slurm_jobs: tp.Sequence[SlurmJob]
) -> dict[config.SSHConfig, list[SlurmJob]]:
    jobs_by_cluster = collections.defaultdict(list)
    for ssh_config, slurm_job in zip(ssh_configs, slurm_jobs):
        jobs_by_cluster[ssh_config].append(slurm_job)
    return jobs_by_cluster


class _BatchedSlurmHandle:
    @functools.partial(
        batching.batch,
        max_batch_size=_BATCHED_BATCH_SIZE,
        batch_timeout=_BATCHED_TIMEOUT,
    )
    @staticmethod
    @backoff.on_exception(backoff.expo, SlurmExecutionError, max_tries=5, max_time=60.0)
    async def _batched_get_state(
        ssh_configs: tp.Sequence[config.SSHConfig],
        slurm_jobs: tp.Sequence[SlurmJob],
    ) -> tp.Sequence[status.SlurmJobState]:
        async def _get_state(
            options: config.SSHConfig, slurm_jobs: tp.Sequence[SlurmJob]
        ) -> tp.Sequence[status.SlurmJobState]:
            result = await get_client().run(
                options,
                [
                    "sacct",
                    "--jobs",
                    ",".join([slurm_job.job_id for slurm_job in slurm_jobs]),
                    "--format",
                    "JobID,State",
                    "--allocations",
                    "--noheader",
                    "--parsable2",
                ],
                check=True,
            )

            assert isinstance(result.stdout, str)
            states_by_job_id = {}
            for line in result.stdout.splitlines():
                job_id, state = line.split("|")
                states_by_job_id[job_id] = status.SlurmJobState.from_slurm_str(state)

            job_states = []
            for slurm_job in slurm_jobs:
                if slurm_job.job_id in states_by_job_id:
                    job_states.append(states_by_job_id[slurm_job.job_id])
                # This is a stupid hack around sacct's inability to display state information for
                # array job elements that haven't begun. We'll assume that if the job ID is not found,
                # and it's an array job, then it's pending.
                elif slurm_job.is_array_job:
                    job_states.append(status.SlurmJobState.PENDING)
                else:
                    raise SlurmExecutionError(f"Failed to find job state info for {slurm_job!r}")
            return job_states

        # Group Slurm jobs by their cluster so we can batch requests
        jobs_by_cluster = _group_by_ssh_configs(ssh_configs, slurm_jobs)

        # Async get state for each cluster
        job_states_per_cluster = await asyncio.gather(*[
            _get_state(options, jobs) for options, jobs in jobs_by_cluster.items()
        ])

        # Reconstruct the job states by cluster
        job_states_by_cluster = {}
        for ssh_config, job_states in zip(ssh_configs, job_states_per_cluster):
            job_states_by_cluster[ssh_config] = dict(zip(jobs_by_cluster[ssh_config], job_states))

        # Reconstruct the job states in the original order
        job_states = []
        for ssh_config, slurm_job in zip(ssh_configs, slurm_jobs):
            job_states.append(job_states_by_cluster[ssh_config][slurm_job])  # type: ignore
        return job_states

    @functools.partial(
        batching.batch,
        max_batch_size=_BATCHED_BATCH_SIZE,
        batch_timeout=_BATCHED_TIMEOUT,
    )
    @staticmethod
    async def _batched_cancel(
        ssh_configs: tp.Sequence[config.SSHConfig],
        slurm_jobs: tp.Sequence[SlurmJob],
    ) -> tp.Sequence[None]:
        async def _cancel(options: config.SSHConfig, slurm_jobs: tp.Sequence[SlurmJob]) -> None:
            await get_client().run(
                options,
                ["scancel", " ".join([slurm_job.job_id for slurm_job in slurm_jobs])],
                check=True,
            )

        jobs_by_cluster = _group_by_ssh_configs(ssh_configs, slurm_jobs)
        return await asyncio.gather(*[
            _cancel(options, job_ids) for options, job_ids in jobs_by_cluster.items()
        ])


@dataclasses.dataclass(frozen=True, kw_only=True)
class SlurmHandle(_BatchedSlurmHandle, tp.Generic[SlurmJobT]):
    """A handle for referring to the launched container."""

    experiment_id: int
    ssh: config.SSHConfig
    slurm_job: Descriptor[SlurmJobT, str] = SlurmJobDescriptor[SlurmJobT]()
    job_name: str  # XManager job name associated with this handle

    @backoff.on_predicate(
        backoff.constant,
        lambda state: state in status.SlurmActiveJobStates,
        jitter=None,
        interval=_POLL_INTERVAL,
    )
    async def wait(self) -> status.SlurmJobState:
        return await self.get_state()

    async def stop(self) -> None:
        await self._batched_cancel(self.ssh, self.slurm_job)

    async def get_state(self) -> status.SlurmJobState:
        return await self._batched_get_state(self.ssh, self.slurm_job)

    async def logs(
        self, *, num_lines: int, block_size: int, wait: bool, follow: bool, raw: bool = False
    ) -> tp.AsyncGenerator[tp.Union[str, ConsoleRenderable], None]:
        experiment_dir = await get_client().experiment_dir(self.ssh, self.experiment_id)
        file = experiment_dir / f"slurm-{self.slurm_job.job_id}.out"
        fs = await get_client().fs(self.ssh)

        if wait:
            while not (await fs.exists(file)):
                await asyncio.sleep(5)

        file_size = await fs.size(file)
        assert file_size is not None

        async with await fs.open(file, "rb") as remote_file:
            data = b""
            lines = []
            position = file_size

            while len(lines) <= num_lines and position > 0:
                read_size = min(block_size, position)
                position -= read_size
                await remote_file.seek(position)
                chunk = await remote_file.read(read_size)
                data = chunk + data
                lines = data.splitlines()

            if position <= 0:
                if raw:
                    yield "\033[31mBEGINNING OF FILE\033[0m\n"
                else:
                    yield Rule("[bold red]BEGINNING OF FILE[/bold red]")
            for line in lines[-num_lines:]:
                if raw:
                    yield line.decode("utf-8", errors="replace") + "\n"
                else:
                    yield Text.from_ansi(line.decode("utf-8", errors="replace"))

            if (await self.get_state()) not in status.SlurmActiveJobStates:
                if raw:
                    yield "\033[31mEND OF FILE\033[0m\n"
                    return
                else:
                    yield Rule("[bold red]END OF FILE[/bold red]")
                    return

            if not follow:
                return

            await remote_file.seek(file_size)
            while True:
                if new_data := (await remote_file.read(block_size)):
                    if raw:
                        yield new_data.decode("utf-8", errors="replace")
                    else:
                        yield Text.from_ansi(new_data.decode("utf-8", errors="replace"))
                else:
                    await asyncio.sleep(0.25)


class CompletedProcess(tp.Protocol):
    returncode: int | None
    stdout: bytes | str
    stderr: bytes | str


@functools.cache
def get_template_env(runtime: config.ContainerRuntime) -> j2.Environment:
    template_loader = j2.PackageLoader("xm_slurm", "templates/slurm")
    template_env = j2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=False)

    def _raise_template_exception(msg: str) -> None:
        raise j2.TemplateRuntimeError(msg)

    template_env.globals["raise"] = _raise_template_exception
    template_env.globals["operator"] = operator

    # Iterate over stdlib files and insert them into the template environment
    stdlib = []
    for file in importlib.resources.files("xm_slurm.templates.slurm.library").iterdir():
        if not file.is_file() or not file.name.endswith(".bash"):
            continue
        stdlib.append(file.read_text())
    template_env.globals["stdlib"] = stdlib

    entrypoint_template = template_env.get_template("entrypoint.bash.j2")
    template_env.globals.update(entrypoint_template.module.__dict__)

    match runtime:
        case config.ContainerRuntime.SINGULARITY | config.ContainerRuntime.APPTAINER:
            runtime_template = template_env.get_template("runtimes/apptainer.bash.j2")
        case config.ContainerRuntime.PODMAN:
            runtime_template = template_env.get_template("runtimes/podman.bash.j2")
        case _:
            raise NotImplementedError(f"Container runtime {runtime} is not implemented.")
    template_env.globals.update(runtime_template.module.__dict__)

    return template_env


class SlurmSSHClient(asyncssh.SSHClient):
    """SSHClient that handles keyboard-interactive 2FA authentication."""

    _kbdint_auth_lock: tp.ClassVar[asyncio.Lock] = asyncio.Lock()
    _host: str

    def __init__(self, host: str):
        self._host = host

    def kbdint_auth_requested(self) -> MaybeAwait[str | None]:
        return ""

    async def kbdint_challenge_received(
        self, name: str, instructions: str, lang: str, prompts: KbdIntPrompts
    ) -> MaybeAwait[KbdIntResponse | None]:
        """Handle 2FA prompts by prompting user for input."""
        del name, lang
        if not sys.stdin.isatty():
            raise SlurmExecutionError(
                f"Two-factor authentication is not supported for non-interactive sessions on {self._host}"
            )

        async with self._kbdint_auth_lock:
            if len(prompts) > 0:
                console.rule(f"Two-Factor Authentication for {self._host}")

            if instructions:
                console.print(instructions, style="bold yellow")

            responses = []
            for prompt, echo in prompts:
                # Manually disable password authentication
                if prompt.strip() == "Password:":
                    return None

                try:
                    response = await asyncio.to_thread(
                        console.input,
                        f"{prompt}\a",
                        password=not echo,
                    )
                except (EOFError, KeyboardInterrupt):
                    console.print("\n[red]Authentication cancelled[/red]")
                    return None
                else:
                    responses.append(response)

            return responses


class SlurmExecutionClient:
    def __init__(self):
        self._remote_connections = dict[config.SSHConfig, asyncssh.SSHClientConnection]()
        self._remote_connection_locks = collections.defaultdict(asyncio.Lock)
        self._remote_filesystems = dict[config.SSHConfig, filesystems.AsyncSSHFileSystem]()

        self._local_fs = filesystems.AsyncLocalFileSystem()

    @backoff.on_exception(backoff.expo, asyncio.exceptions.TimeoutError, max_tries=5, max_time=60.0)
    async def _local_run(  # type: ignore
        self,
        command: str,
        *,
        check: bool = False,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess[str]:
        process = await asyncio.subprocess.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            # Filter out all SLURM_ environment variables as this could be running on a
            # compute node and xm-slurm should act stateless.
            env=dict(filter(lambda x: not x[0].startswith("SLURM_"), os.environ.items())),
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)

        stdout = stdout.decode("utf-8").strip() if stdout else ""
        stderr = stderr.decode("utf-8").strip() if stderr else ""

        assert process.returncode is not None
        if check and process.returncode != 0:
            raise RuntimeError(f"Command failed with return code {process.returncode}: {command}\n")

        return subprocess.CompletedProcess[str](command, process.returncode, stdout, stderr)

    @backoff.on_exception(backoff.expo, asyncssh.Error, max_tries=5, max_time=60.0)
    async def _remote_run(  # type: ignore
        self,
        ssh_config: config.SSHConfig,
        command: str,
        *,
        check: bool = False,
        timeout: float | None = None,
    ) -> asyncssh.SSHCompletedProcess:
        client = await self._connection(ssh_config)
        return await client.run(command, check=check, timeout=timeout)

    @functools.cache
    def _is_ssh_config_local(self, ssh_config: config.SSHConfig) -> bool:
        """A best effort check to see if the SSH config is local so we can bypass ssh."""
        # TODO(jfarebro): Make async

        # We can't verify the connection so bail out
        if ssh_config.public_key is None:
            return False
        if "SSH_CONNECTION" not in os.environ:
            return False

        def _is_host_local(host: str) -> bool:
            nonlocal ssh_config
            assert ssh_config.public_key is not None

            if shutil.which("ssh-keyscan") is None:
                return False

            keyscan_result = utils.run_command(
                ["ssh-keyscan", "-t", ssh_config.public_key.algorithm, host],
                return_stdout=True,
            )

            if keyscan_result.returncode != 0:
                return False

            try:
                key = mit.one(
                    filter(
                        lambda x: not x.startswith("#"), keyscan_result.stdout.strip().split("\n")
                    )
                )
                _, algorithm, key = key.split(" ")

                if (
                    algorithm == ssh_config.public_key.algorithm
                    and key == ssh_config.public_key.key
                ):
                    return True

            except Exception:
                pass

            return False

        # 1): we're directly connected to the host
        ssh_connection_str = os.environ["SSH_CONNECTION"]
        _, _, server_ip, _ = ssh_connection_str.split()

        logger.debug("Checking if SSH_CONNECTION server %s is local", server_ip)
        if _is_host_local(server_ip):
            return True

        # 2): we're in a Slurm job and the submission host is the host
        if "SLURM_JOB_ID" in os.environ and "SLURM_SUBMIT_HOST" in os.environ:
            submit_host = os.environ["SLURM_SUBMIT_HOST"]
            logger.debug("Checking if SLURM_SUBMIT_HOST %s is local", submit_host)
            if _is_host_local(submit_host):
                return True
        elif "SLURM_JOB_ID" in os.environ and shutil.which("scontrol") is not None:
            # Stupid edge case where if you run srun SLURM_SUBMIT_HOST isn't forwarded
            # so we'll parse it from scontrol...
            scontrol_result = utils.run_command(
                ["scontrol", "show", "job", os.environ["SLURM_JOB_ID"]],
                return_stdout=True,
            )
            if scontrol_result.returncode != 0:
                return False

            match = re.search(
                r"AllocNode:Sid=(?P<host>[^ ]+):\d+", scontrol_result.stdout.strip(), re.MULTILINE
            )
            if match is not None:
                host = match.group("host")
                logger.debug("Checking if AllocNode %s is local", host)
                if _is_host_local(host):
                    return True

        return False

    @functools.cache
    @utils.reawaitable
    async def _state_dir(self, ssh_config: config.SSHConfig) -> pathlib.Path:
        state_dirs = [
            ("XM_SLURM_STATE_DIR", ""),
            ("XDG_STATE_HOME", "xm-slurm"),
            ("HOME", ".local/state/xm-slurm"),
        ]

        for env_var, subpath in state_dirs:
            cmd = await self.run(ssh_config, f"printenv {env_var}", check=False)
            assert isinstance(cmd.stdout, str)
            if cmd.returncode == 0:
                return pathlib.Path(cmd.stdout.strip()) / subpath

        raise SlurmExecutionError(
            "Failed to find a valid state directory for XManager. "
            "We weren't able to resolve any of the following paths: "
            f"{', '.join(env_var + ('/' + subpath if subpath else '') for env_var, subpath in state_dirs)}."
        )

    @functools.cached_property
    def _ssh_config_dirs(self) -> list[pathlib.Path]:
        ssh_config_paths = []

        if (ssh_config_path := pathlib.Path.home() / ".ssh" / "config").exists():
            ssh_config_paths.append(ssh_config_path)
        if (xm_ssh_config_var := os.environ.get("XM_SLURM_SSH_CONFIG")) and (
            xm_ssh_config_path := pathlib.Path(xm_ssh_config_var).expanduser()
        ).exists():
            ssh_config_paths.append(xm_ssh_config_path)

        return ssh_config_paths

    async def experiment_dir(
        self, ssh_config: config.SSHConfig, experiment_id: int
    ) -> pathlib.Path:
        return (await self._state_dir(ssh_config)) / f"{experiment_id:08d}"

    async def run(
        self,
        ssh_config: config.SSHConfig,
        command: xm.SequentialArgs | str | tp.Sequence[str],
        *,
        check: bool = False,
        timeout: float | None = None,
    ) -> CompletedProcess:
        if isinstance(command, xm.SequentialArgs):
            command = command.to_list()
        if not isinstance(command, str) and isinstance(command, collections.abc.Sequence):
            command = shlex.join(command)
        assert isinstance(command, str)

        if self._is_ssh_config_local(ssh_config):
            logger.debug("Running command locally: %s", command)
            return await self._local_run(command, check=check, timeout=timeout)  # type: ignore
        else:
            logger.debug(
                "Running command on %s: %s", ", ".join(map(str, ssh_config.endpoints)), command
            )
            return await self._remote_run(ssh_config, command, check=check, timeout=timeout)  # type: ignore

    async def fs(self, ssh_config: config.SSHConfig) -> filesystems.AsyncFileSystem:
        if self._is_ssh_config_local(ssh_config):
            return self._local_fs

        if ssh_config not in self._remote_filesystems:
            self._remote_filesystems[ssh_config] = filesystems.AsyncSSHFileSystem(
                await (await self._connection(ssh_config)).start_sftp_client()
            )
        return self._remote_filesystems[ssh_config]

    async def _connection(self, ssh_config: config.SSHConfig) -> asyncssh.SSHClientConnection:
        async def _connect_to_endpoint(
            endpoint: config.Endpoint,
        ) -> asyncssh.SSHClientConnection:
            __tracebackhide__ = True
            try:
                config = asyncssh.config.SSHClientConfig.load(
                    None,
                    self._ssh_config_dirs,
                    True,
                    True,
                    True,
                    getpass.getuser(),
                    ssh_config.user or (),
                    endpoint.hostname,
                    endpoint.port or (),
                )
                if config.get("Hostname") is None and (
                    constants.DOMAIN_NAME_REGEX.match(endpoint.hostname)
                    or constants.IPV4_REGEX.match(endpoint.hostname)
                    or constants.IPV6_REGEX.match(endpoint.hostname)
                ):
                    config._options["Hostname"] = endpoint.hostname
                elif config.get("Hostname") is None:
                    raise RuntimeError(
                        f"Failed to parse hostname from host `{endpoint.hostname}` using "
                        f"SSH configs: {', '.join(map(str, self._ssh_config_dirs))} and "
                        f"provided hostname `{endpoint.hostname}` isn't a valid domain name "
                        "or IPv{4,6} address."
                    )

                if config.get("User") is None:
                    raise RuntimeError(
                        f"We could not find a user for the cluster configuration: `{endpoint.hostname}`. "
                        "No user was specified in the configuration and we could not parse "
                        f"any users for host `{config.get('Hostname')}` from the SSH configs: "
                        f"{', '.join(map(lambda h: f'`{h}`', self._ssh_config_dirs))}. Please either specify a user "
                        "in the configuration or add a user to your SSH configuration under the block "
                        f"`Host {config.get('Hostname')}`."
                    )

                options = await asyncssh.SSHClientConnectionOptions.construct(
                    config=None,
                    disable_trivial_auth=True,
                    password_auth=False,
                    server_host_key_algs=ssh_config.public_key.algorithm
                    if ssh_config.public_key
                    else None,
                    login_timeout=60 * 10,  # 10 minutes
                    known_hosts=ssh_config.known_hosts,
                )
                options.prepare(last_config=config)

                conn, _ = await asyncssh.create_connection(
                    lambda: SlurmSSHClient(endpoint.hostname),
                    host=endpoint.hostname,
                    port=endpoint.port or (),
                    options=options,
                )
                return conn
            except asyncssh.misc.PermissionDenied as ex:
                raise SlurmExecutionError(
                    f"Permission denied connecting to {endpoint.hostname}"
                ) from ex
            except asyncssh.misc.ConnectionLost as ex:
                raise SlurmExecutionError(f"Connection lost to host {endpoint.hostname}") from ex
            except asyncssh.misc.HostKeyNotVerifiable as ex:
                raise SlurmExecutionError(
                    f"Cannot verify the public key for host {endpoint.hostname}"
                ) from ex
            except asyncssh.misc.KeyExchangeFailed as ex:
                raise SlurmExecutionError(
                    f"Failed to exchange keys with host {endpoint.hostname}"
                ) from ex
            except asyncssh.Error as ex:
                raise SlurmExecutionError(
                    f"SSH connection error when connecting to {endpoint.hostname}"
                ) from ex

        conn = self._remote_connections.get(ssh_config)
        if conn is not None and not conn.is_closed():
            return conn

        async with self._remote_connection_locks[ssh_config]:
            conn = self._remote_connections.get(ssh_config)
            if conn is not None and not conn.is_closed():
                return conn

            exceptions: list[Exception] = []
            for endpoint in ssh_config.endpoints:
                try:
                    conn = await _connect_to_endpoint(endpoint)
                except Exception as ex:
                    exceptions.append(ex)
                else:
                    self._remote_connections[ssh_config] = conn
                    return conn

            if sys.version_info >= (3, 11):
                raise ExceptionGroup("Failed to connect to all hosts", exceptions)  # noqa: F821
            raise exceptions[-1]

    async def _submission_script_template(
        self,
        *,
        job: xm.Job | xm.JobGroup,
        dependency: dependencies.SlurmJobDependency | None = None,
        cluster: config.SlurmClusterConfig,
        args: tp.Mapping[str, tp.Any] | tp.Sequence[tp.Mapping[str, tp.Any]] | None,
        experiment_id: int,
        identity: str | None,
    ) -> str:
        # Sanitize args
        match args:
            case None:
                args = {}
            case collections.abc.Mapping():
                args = dict(args)
            case collections.abc.Sequence():
                assert all(isinstance(trial, collections.abc.Mapping) for trial in args)
                args = [dict(trial) for trial in args]
            case _:
                raise ValueError("Invalid args type")
        args = tp.cast(dict[str, tp.Any] | list[dict[str, tp.Any]], args)

        template_env = get_template_env(cluster.runtime)
        template_context = dict(
            dependency=dependency,
            cluster=cluster,
            experiment_id=experiment_id,
            identity=identity,
        )

        # Sanitize job groups
        if isinstance(job, xm.JobGroup) and len(job.jobs) == 1:
            job = tp.cast(xm.Job, list(job.jobs.values())[0])
        elif isinstance(job, xm.JobGroup) and len(job.jobs) == 0:
            raise ValueError("Job group must have at least one job")

        match job:
            case xm.Job() as job_array if isinstance(args, collections.abc.Sequence):
                assert isinstance(args, list)
                template = template_env.get_template("job-array.bash.j2")
                sequential_args = [
                    xm.SequentialArgs.from_collection(trial.get("args")) for trial in args
                ]
                env_vars = [trial.get("env_vars") for trial in args]
                if any(env_vars):
                    raise NotImplementedError(
                        "Job arrays over environment variables are not yet supported."
                    )

                return template.render(
                    job=job_array, args=sequential_args, env_vars=env_vars, **template_context
                )
            case xm.Job() if isinstance(args, collections.abc.Mapping):
                assert isinstance(args, dict)
                template = template_env.get_template("job.bash.j2")
                sequential_args = xm.SequentialArgs.from_collection(args.get("args"))
                env_vars = args.get("env_vars")
                return template.render(
                    job=job, args=sequential_args, env_vars=env_vars, **template_context
                )
            case xm.JobGroup() as job_group if isinstance(args, collections.abc.Mapping):
                assert isinstance(args, dict)
                template = template_env.get_template("job-group.bash.j2")
                sequential_args = {
                    job_name: {
                        "args": args.get(job_name, {}).get("args"),
                    }
                    for job_name in job_group.jobs.keys()
                }
                env_vars = {
                    job_name: args.get(job_name, {}).get("env_vars")
                    for job_name in job_group.jobs.keys()
                }
                return template.render(
                    job_group=job_group, args=sequential_args, env_vars=env_vars, **template_context
                )
            case _:
                raise ValueError(f"Unsupported job type: {type(job)}")

    @tp.overload
    async def launch(
        self,
        *,
        cluster: config.SlurmClusterConfig,
        job: xm.JobGroup,
        dependency: dependencies.SlurmJobDependency | None = None,
        args: tp.Mapping[str, job_blocks.JobArgs] | None,
        experiment_id: int,
        identity: str | None = ...,
    ) -> SlurmHandle: ...

    @tp.overload
    async def launch(
        self,
        *,
        cluster: config.SlurmClusterConfig,
        job: xm.Job,
        dependency: dependencies.SlurmJobDependency | None = None,
        args: tp.Sequence[job_blocks.JobArgs],
        experiment_id: int,
        identity: str | None = ...,
    ) -> list[SlurmHandle]: ...

    @tp.overload
    async def launch(
        self,
        *,
        cluster: config.SlurmClusterConfig,
        job: xm.Job,
        dependency: dependencies.SlurmJobDependency | None = None,
        args: job_blocks.JobArgs,
        experiment_id: int,
        identity: str | None = ...,
    ) -> SlurmHandle: ...

    async def launch(
        self,
        *,
        cluster: config.SlurmClusterConfig,
        job: xm.Job | xm.JobGroup,
        dependency: dependencies.SlurmJobDependency | None = None,
        args: tp.Mapping[str, job_blocks.JobArgs]
        | tp.Sequence[job_blocks.JobArgs]
        | job_blocks.JobArgs
        | None,
        experiment_id: int,
        identity: str | None = None,
    ):
        submission_script = await self._submission_script_template(
            job=job,
            dependency=dependency,
            cluster=cluster,
            args=args,
            experiment_id=experiment_id,
            identity=identity,
        )
        logger.debug("Slurm submission script:\n%s", submission_script)
        submission_script_hash = hashlib.blake2s(submission_script.encode()).hexdigest()[:8]
        submission_script_path = f"submission-script-{submission_script_hash}.sh"

        fs = await self.fs(cluster.ssh)

        template_dir = await self.experiment_dir(cluster.ssh, experiment_id)

        await fs.makedirs(template_dir, exist_ok=True)
        await fs.write(template_dir / submission_script_path, submission_script.encode())

        # Construct and run command on the cluster
        command = f"sbatch --chdir {template_dir.as_posix()} --parsable {submission_script_path}"
        result = await self.run(cluster.ssh, command)
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to schedule job on {', '.join(map(str, cluster.ssh.endpoints))}: {result.stderr}"
            )

        assert isinstance(result.stdout, str)
        slurm_job_id, *_ = result.stdout.split(",")
        slurm_job_id = slurm_job_id.strip()

        console.log(
            f"[magenta]:rocket: Job [cyan]{slurm_job_id}[/cyan] will be launched on "
            f"[cyan]{cluster.name}[/cyan] "
        )

        # If we scheduled an array job make sure to return a list of handles
        # The indexing is always sequential in 0, 1, ..., n - 1
        if isinstance(job, xm.Job) and isinstance(args, collections.abc.Sequence):
            assert job.name is not None
            return [
                SlurmHandle(
                    experiment_id=experiment_id,
                    ssh=cluster.ssh,
                    slurm_job=f"{slurm_job_id}_{array_index}",
                    job_name=job.name,
                )
                for array_index in range(len(args))
            ]
        elif isinstance(job, xm.Job):
            assert job.name is not None
            return SlurmHandle(
                experiment_id=experiment_id,
                ssh=cluster.ssh,
                slurm_job=slurm_job_id,
                job_name=job.name,
            )
        elif isinstance(job, xm.JobGroup):
            # TODO: make this work for actual job groups.
            job = tp.cast(xm.Job, mit.one(job.jobs.values()))
            assert isinstance(job, xm.Job)
            assert job.name is not None
            return SlurmHandle(
                experiment_id=experiment_id,
                ssh=cluster.ssh,
                slurm_job=slurm_job_id,
                job_name=job.name,
            )
        else:
            raise ValueError(f"Unsupported job type: {type(job)}")

    def __del__(self):
        for fs in self._remote_filesystems.values():
            del fs
        for conn in self._remote_connections.values():
            conn.close()
            del conn


@functools.cache
def get_client() -> SlurmExecutionClient:
    return SlurmExecutionClient()


@tp.overload
async def launch(
    *,
    job: xm.JobGroup,
    dependency: dependencies.SlurmJobDependency | None = None,
    args: tp.Mapping[str, job_blocks.JobArgs],
    experiment_id: int,
    identity: str | None = ...,
) -> SlurmHandle: ...


@tp.overload
async def launch(
    *,
    job: xm.Job,
    dependency: dependencies.SlurmJobDependency | None = None,
    args: tp.Sequence[job_blocks.JobArgs],
    experiment_id: int,
    identity: str | None = ...,
) -> list[SlurmHandle]: ...


@tp.overload
async def launch(
    *,
    job: xm.Job,
    dependency: dependencies.SlurmJobDependency | None = None,
    args: job_blocks.JobArgs,
    experiment_id: int,
    identity: str | None = ...,
) -> SlurmHandle: ...


async def launch(
    *,
    job: xm.Job | xm.JobGroup,
    dependency: dependencies.SlurmJobDependency | None = None,
    args: tp.Mapping[str, job_blocks.JobArgs]
    | tp.Sequence[job_blocks.JobArgs]
    | job_blocks.JobArgs,
    experiment_id: int,
    identity: str | None = None,
) -> SlurmHandle | list[SlurmHandle]:
    match job:
        case xm.Job() as job:
            if not isinstance(job.executor, executors.Slurm):
                raise ValueError("Job must have a Slurm executor")
            job_requirements = job.executor.requirements
            cluster = job_requirements.cluster
            if cluster is None:
                raise ValueError("Job must have a cluster requirement")
            if cluster.validate is not None:
                cluster.validate(job)

            return await get_client().launch(
                cluster=cluster,
                job=job,
                dependency=dependency,
                args=tp.cast(job_blocks.JobArgs | tp.Sequence[job_blocks.JobArgs], args),
                experiment_id=experiment_id,
                identity=identity,
            )
        case xm.JobGroup() as job_group:
            job_group_executors = set()
            job_group_clusters = set()
            for job_item in job_group.jobs.values():
                if not isinstance(job_item, xm.Job):
                    raise ValueError("Job group must contain only jobs")
                if not isinstance(job_item.executor, executors.Slurm):
                    raise ValueError("Job must have a Slurm executor")
                if job_item.executor.requirements.cluster is None:
                    raise ValueError("Job must have a cluster requirement")
                if job_item.executor.requirements.cluster.validate is not None:
                    job_item.executor.requirements.cluster.validate(job_item)
                job_group_clusters.add(job_item.executor.requirements.cluster)
                job_group_executors.add(id(job_item.executor))
            if len(job_group_executors) != 1:
                raise ValueError("Job group must have the same executor for all jobs")
            if len(job_group_clusters) != 1:
                raise ValueError("Job group must have the same cluster for all jobs")

            return await get_client().launch(
                cluster=job_group_clusters.pop(),
                job=job_group,
                dependency=dependency,
                args=tp.cast(tp.Mapping[str, job_blocks.JobArgs], args),
                experiment_id=experiment_id,
                identity=identity,
            )
