import logging
import os


def init_logger(name: str):
    logging.basicConfig(
        level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        force=True,
    )
    for noisy in ("botocore", "boto3", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return logging.getLogger(name)


def log_with_event(level_fn, msg, event):
    level_fn(f"{msg} | event={event}")
