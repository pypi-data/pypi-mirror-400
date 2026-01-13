from django.db import models

from .core import UuidModel


class CoreHealthcheck(UuidModel):
    """Base Model with uuid."""

    healthcheck_run_datetime = models.DateTimeField(verbose_name="Healthcheck Run Datetime", blank=True, null=True)

    class Meta:
        verbose_name = "Core Healthcheck"
        verbose_name_plural = "Core Healthchecks"

    def __str__(self) -> str:
        return f"{self.id}"
