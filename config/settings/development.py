"""
Development settings.
"""
from .base import *  # noqa: F401, F403
from decouple import config

DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")

# Allow CORS for development
CORS_ALLOW_ALL_ORIGINS = True
