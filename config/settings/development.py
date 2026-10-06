"""
Django settings – development environment overrides.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# ── Debug toolbar (optional – install django-debug-toolbar and add below) ──
# INSTALLED_APPS.append("debug_toolbar")  # noqa: F405
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
# INTERNAL_IPS = ["127.0.0.1"]  # noqa: F405

# ── Email backend – writes to console ─────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
