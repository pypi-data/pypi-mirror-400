import logging

from django.apps import AppConfig

log = logging.getLogger(__name__)


class JfkDjangoCoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "jfk_django_core"
    verbose_name = "JFK Django Core"
