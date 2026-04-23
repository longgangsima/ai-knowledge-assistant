from app.models.api import JobResponse


class InMemoryJobRepository:
    def __init__(self) -> None:
        self._jobs: dict[str, JobResponse] = {}

    async def save(self, job: JobResponse) -> None:
        self._jobs[job.job_id] = job

    async def get(self, job_id: str) -> JobResponse | None:
        return self._jobs.get(job_id)


_job_repository = InMemoryJobRepository()


def get_job_repository() -> InMemoryJobRepository:
    return _job_repository
