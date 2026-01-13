from __future__ import annotations

import logging

from .executor import AtomicExecutor
from .utils import auth_settings_from_env_or_dev_secure

logger = logging.getLogger(__name__)


def create_app():
    auth_settings = auth_settings_from_env_or_dev_secure()
    logger.info(
        "Atomic Executor auth settings (mode=%s, issuer=%s)",
        getattr(auth_settings, "mode", None),
        getattr(auth_settings, "issuer", None),
    )
    return AtomicExecutor().create_app(
        title="JARVIS Atomic Executor",
        auth_settings=auth_settings,
    )


app = create_app()
