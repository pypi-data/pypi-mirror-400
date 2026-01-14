"""Module entry point for nested_python_module testing fixture."""

import logging

from src import func_one  # type: ignore[attr-defined]
from src import func_two  # type: ignore[attr-defined]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Nested Python Module is running.")
    result_one = func_one()
    logger.info("func_one result: %s", {result_one})
    result_two = func_two()
    logger.info("func_two result: %s", {result_two})
    logger.info("Nested Python Module executed successfully.")
