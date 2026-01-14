import hashlib
import os
import tempfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser


def get_file_name() -> Path:
    try:
        name = str(int(datetime.now().timestamp()))
        f, path = tempfile.mkstemp(name)
        os.close(f)
        Path(path).unlink(missing_ok=True)
        path = Path(path).parent
    except Exception:  # noqa: BLE001
        path = Path("/tmp") if os.sep != "\\" else Path(os.path.expandvars("%temp%"))

    project = Path(settings.BASE_DIR).name
    filename = hashlib.md5(project.encode()).hexdigest()
    return path / filename


def humanize_time(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}h {minutes:02}m {seconds:02}s"


class Command(BaseCommand):
    help = "Calculate uptime"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("-s", "--start", action="store_true")
        parser.add_argument("--filename", action="store_true")

    def get_uptime(self, start: bool = False, verbosity: int = 1) -> str:
        file = get_file_name()
        if not file.exists() or start:
            file.touch()
            if verbosity > 1:
                self.stdout.write(f"{'Recreated' if start else 'Created'} {file}\n")
        elif verbosity > 1:
            self.stdout.write(f"Checked {file}\n")

        started_at = file.stat().st_mtime
        return humanize_time(int(datetime.now().timestamp() - started_at))

    def handle(self, *args, **options) -> None:
        filename_only = options.get("filename", False)
        if filename_only:
            self.stdout.write(f"{get_file_name()}\n")
            return

        start = options.get("start", False)
        verbosity = options.get("verbosity", 1)
        self.stdout.write(f"{self.get_uptime(start, verbosity)}\n")
