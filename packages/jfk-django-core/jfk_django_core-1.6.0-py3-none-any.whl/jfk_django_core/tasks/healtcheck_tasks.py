import logging

from celery import shared_task
from django.utils import timezone

from jfk_django_core.models import CoreHealthcheck

log = logging.getLogger(__name__)


@shared_task(ignore_result=False)
def celery_healthcheck_task() -> None:
    core_healthcheck_qs = CoreHealthcheck.objects.all()
    if core_healthcheck_qs.count() == 0:
        CoreHealthcheck.objects.create(healthcheck_run_datetime=timezone.now())
    elif core_healthcheck_qs.count() == 1:
        core_healthcheck = core_healthcheck_qs.first()
        if core_healthcheck is not None:
            core_healthcheck.healthcheck_run_datetime = timezone.now()
            core_healthcheck.save()
    else:
        log.error(f"Found {core_healthcheck_qs.count()} CoreHealthcheck records. Expected 0 or 1.")
        core_healthcheck_qs.delete()
        CoreHealthcheck.objects.create(healthcheck_run_datetime=timezone.now())
