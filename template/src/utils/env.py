from config import get_settings, Environments

settings = get_settings()


def is_test():
    """Check if the current environment is 'test'."""
    return settings.env == Environments.TEST


def is_dev():
    """Check if the current environment is 'development'."""
    return settings.env == Environments.DEVELOPMENT


def is_prod():
    """Check if the current environment is 'production'."""
    return settings.env == Environments.PRODUCTION


def get_env():
    """Get the current environment."""
    return settings.env
