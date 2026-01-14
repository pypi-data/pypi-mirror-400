from importlib.metadata import version

__version__ = version("k3jobq")

from .jobq import (
    EmptyRst,
    Finish,
    run,
    stat,
    JobManager,
    JobWorkerError,
    JobWorkerNotFound,
)

from .works import (
    limit_job_speed,
)

__all__ = [
    "EmptyRst",
    "Finish",
    "run",
    "stat",
    "JobManager",
    "JobWorkerError",
    "JobWorkerNotFound",
    "limit_job_speed",
]
