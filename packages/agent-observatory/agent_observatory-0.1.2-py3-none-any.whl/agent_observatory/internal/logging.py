import logging

# Internal logger for Agent Observatory (library-controlled, fail-open)
logger = logging.getLogger("agent_observatory")


def log_internal_error(msg: str) -> None:
    logger.error(msg)
