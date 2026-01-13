"""CronJob resource builder."""

from __future__ import annotations

from k8smith.core.builder import ResourceBuilder
from k8smith.core.models import CronJobSpec


def build_cronjob(spec: CronJobSpec) -> dict:
    """Build a Kubernetes CronJob resource.

    Note: job_template is handled manually because Kubernetes expects
    the nested structure spec.jobTemplate.spec.template, which can't
    be expressed through ResourceBuilder's simple field routing.

    Args:
        spec: CronJob specification

    Returns:
        Kubernetes CronJob resource as a dict
    """
    resource = ResourceBuilder.build(spec, "batch/v1", "CronJob", skip_fields={"job_template"})
    resource["spec"]["jobTemplate"] = {"spec": {"template": spec.job_template.to_dict()}}

    return resource
