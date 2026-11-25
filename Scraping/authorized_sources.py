
from normalize import normalize_job


def collect_authorized_jobs(jobs, source_name):
    results = []

    for job in jobs:
        results.append(
            normalize_job(job, source_name)
        )

    return results
