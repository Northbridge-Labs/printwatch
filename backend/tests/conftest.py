"""Pytest fixtures shared across the backend."""
import os
import django
import pytest


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()