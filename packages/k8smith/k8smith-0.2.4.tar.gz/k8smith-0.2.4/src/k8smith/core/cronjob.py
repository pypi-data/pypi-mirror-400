"""CronJob resource builder."""

from __future__ import annotations

from k8smith.core.models import CronJobSpec


def build_cronjob(spec: CronJobSpec) -> dict:
    """Build a Kubernetes CronJob resource.

    Args:
        spec: CronJob specification

    Returns:
        Kubernetes CronJob resource as a dict
    """
    cronjob: dict = {
        "apiVersion": "batch/v1",
        "kind": "CronJob",
        "metadata": {
            "name": spec.name,
            "namespace": spec.namespace,
        },
        "spec": {
            "schedule": spec.schedule,
            "jobTemplate": {
                "spec": {
                    "template": spec.job_template.to_dict(),
                },
            },
        },
    }

    # Add optional metadata fields
    if spec.labels:
        cronjob["metadata"]["labels"] = spec.labels
    if spec.annotations:
        cronjob["metadata"]["annotations"] = spec.annotations

    # Add optional spec fields
    if spec.concurrency_policy:
        cronjob["spec"]["concurrencyPolicy"] = spec.concurrency_policy
    if spec.successful_jobs_history_limit is not None:
        cronjob["spec"]["successfulJobsHistoryLimit"] = spec.successful_jobs_history_limit
    if spec.failed_jobs_history_limit is not None:
        cronjob["spec"]["failedJobsHistoryLimit"] = spec.failed_jobs_history_limit
    if spec.starting_deadline_seconds is not None:
        cronjob["spec"]["startingDeadlineSeconds"] = spec.starting_deadline_seconds
    if spec.suspend is not None:
        cronjob["spec"]["suspend"] = spec.suspend
    if spec.time_zone:
        cronjob["spec"]["timeZone"] = spec.time_zone

    return cronjob
