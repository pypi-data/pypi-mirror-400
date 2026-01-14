import gzip
import pickle
from typing import Dict, Tuple, List
from functools import reduce

from blueness import module
from bluer_options import string
from bluer_options.logger.config import log_list, shorten_text
from bluer_objects import file, path

from bluer_agent import NAME, ICON
from bluer_agent.host import signature
from bluer_agent.logger import logger


NAME = module.name(__file__, NAME)

"""
using gzip-compressed pickle:
    - binary
    - compact
    - easy to load back in Python
"""


def export(
    results: Dict[str, str],
    filename,
) -> bool:
    filename = file.add_extension(filename, "html")

    success, report = file.load_text(
        file.absolute(
            "../assets/review.html",
            file.path(__file__),
        )
    )
    if not success:
        return success

    report = [
        line.replace(
            "title:::",
            path.name(file.path(filename)),
        ).replace(
            "signature:::",
            "{} {}".format(
                ICON,
                " | ".join(signature()),
            ),
        )
        for line in report
    ]

    content = reduce(
        lambda x, y: x + y,
        [
            [
                "<details>",
                f'    <summary><a href="{key}">{key}</a></summary>',
                '    <div class="value">{}</div>'.format(value.replace("\n", " ")),
                "</details>",
            ]
            for key, value in results.items()
        ],
        [],
    )

    report = reduce(
        lambda x, y: x + y,
        [content if "content:::" in line else [line] for line in report],
        [],
    )

    if not file.save_text(filename, report):
        return False

    logger.info(
        "{}.export: {} page(s) -> {} [{}]".format(
            NAME,
            len(results),
            filename,
            string.pretty_bytes(file.size(filename)),
        )
    )
    return True


def load(filename: str) -> Tuple[bool, Dict[str, str]]:
    try:
        with gzip.open(filename, "rb") as f:
            payload = pickle.load(f)
    except Exception as e:
        logger.error(e)
        return False, {}

    if (
        not isinstance(payload, dict)
        or payload.get("format") != "site_text_collector"
        or "results" not in payload
    ):
        logger.error("unrecognized binary format.")
        return False, {}

    results = payload["results"]

    log_list(
        logger,
        "loaded from {} [{}]".format(
            filename,
            string.pretty_bytes(file.size(filename)),
        ),
        [
            "{}: {}".format(
                key,
                shorten_text(text.replace("\n", " ")),
            )
            for key, text in results.items()
        ],
        "page(s)",
    )

    return True, results


def save(
    results: Dict[str, str],
    filename: str,
) -> bool:
    if not results:
        logger.warning("no pages collected; nothing to save.")
        return True

    payload = {
        "format": "site_text_collector",
        "version": 1,
        "results": results,
    }
    try:
        with gzip.open(filename, "wb") as f:
            pickle.dump(payload, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        logger.error(e)
        return False

    logger.info(
        "{}.save: {} page(s) -> {} [{}]".format(
            NAME,
            len(results),
            filename,
            string.pretty_bytes(file.size(filename)),
        )
    )
    return True
