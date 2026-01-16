#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import threading
import webbrowser


def open_swagger():
    # Delay slightly so the server has time to start
    import time
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:8000/swagger/")


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sems_auth_service.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Auto-open Swagger when running the dev server
    if len(sys.argv) > 1 and sys.argv[1] == "runserver":
        threading.Thread(target=open_swagger, daemon=True).start()

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
