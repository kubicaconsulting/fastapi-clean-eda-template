import os
from functools import lru_cache

from dynaconf import Dynaconf
from pydantic import ValidationError

from .schemas import Settings

# Define the base directory
root_path = os.path.dirname(os.path.realpath(__file__))

settings = Dynaconf(
    root_path=root_path,
    envvar_prefix=False,
    load_dotenv=False,
    merge_enabled=True,
    env_switcher="ENV",
    environments=True,
    settings_files=[
        "settings.json",
        ".secrets.json",
    ],
    validate_only_current_env=True,
    ignore_unknown_envvars=False,  # Keep os environment variables
)


@lru_cache
def get_settings():
    """Get cached and validated settings instance."""
    data = {k.lower(): v for k, v in settings.items() if v is not None}

    try:
        return Settings(**data)
    except ValidationError as e:
        # Fail fast with readable output
        raise RuntimeError(f"Invalid configuration:\n{e}") from e
