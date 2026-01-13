import json
import logging
import os

logger = logging.getLogger(__name__)


def write_report(output_file: str, data: dict) -> None:
    """
    Write the broken links report to a JSON file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(
        f"📊 Broken links report written to: {os.path.abspath(output_file)}"
    )
