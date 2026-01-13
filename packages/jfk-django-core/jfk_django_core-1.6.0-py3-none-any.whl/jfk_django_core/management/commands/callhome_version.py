import logging

from django.core.management.base import BaseCommand

from jfk_django_core.callhome import callhome_version

log = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Callhome version information"

    def handle(self, *args, **kwargs):
        try:
            self.stdout.write(self.style.HTTP_INFO("Calling Home Version..."))
            callhome_version()
        except Exception:
            log.exception(
                "Failed to run callhome_version command!",
            )
            self.stdout.write(self.style.ERROR("Failed to run callhome_version command!"))
