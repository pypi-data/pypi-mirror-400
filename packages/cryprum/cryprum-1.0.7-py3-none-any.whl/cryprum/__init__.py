import logging

logger = logging.getLogger("cryprum")


try:
    from .api import Client
    from .asyncapi import AsyncClient
except ImportError as e:
    logger.exception(e)

    def Client(*args, **kwargs):
        import sys

        print(
            "The cryprum client could not init because the required "
            "dependencies were not installed.\nMake sure you've installed "
            "everything with: pip install cryprum"
        )
        sys.exit(1)

    AsyncClient = Client

__all__ = ["Client", "AsyncClient"]
