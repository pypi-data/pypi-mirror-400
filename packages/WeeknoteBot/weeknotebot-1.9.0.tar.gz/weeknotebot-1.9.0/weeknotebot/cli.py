import datetime
import json
import logging
import os
from pathlib import Path

import click
from rich.logging import RichHandler

from weeknotebot.config_manager import get_config_schema
from weeknotebot.generator import write_weeknote

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


FORMAT = "%(message)s"
logging.basicConfig(
    level=LOG_LEVEL, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

DEFAULT_CONFIG = {
    "generator": {
        "tag": "week note",
        "output": "weeknotes/",
        "fix_links_label": "Fix Links",
        "type_weeknote": "weeknote",
    },
    "empty_section": ["Post Recommendation", "Podcast Episode Recommendation"],
    "feeds": [
        {
            "title": "My new post from my blog",
            "url": "https://www.fundor333.com/index.xml",
        },
        {
            "title": "My new post from my newsletter",
            "url": "https://newsletter.digitaltearoom.com/rss/",
        },
    ],
    "fix_links": [
        {"title": "My blog", "url": "https://www.fundor333.com"},
        {
            "title": "My newsletter",
            "url": "https://newsletter.digitaltearoom.com",
        },
        {"title": "Support me", "url": "https://ko-fi.com/fundor333"},
    ],
    "goodread": {
        "user_id": "5312887-matteo",
        "shelf_name_code": "currently-reading",
        "shelf_name_label": "Currently Reading",
    },
    "anilist": {
        "user_id": "fundor333",
    },
}


def doesFileExists(filePathAndName):
    return os.path.exists(filePathAndName)


@click.command()
@click.option(
    "--configuration",
    "-config",
    default="~/.config/weeknote_bot/config.json",
    type=str,
    required=False,
    help="Path to the configuration file.",
)
@click.option(
    "--today",
    "-t",
    default=None,
    type=str,
    required=False,
    help="Today's date in the format YYYY/MM/DD.",
)
def cli(configuration: str, today: str) -> None:
    configuration = os.path.expanduser(configuration)
    if today is None:
        today = datetime.datetime.now()
    else:
        today = datetime.datetime.strptime(today, "%Y/%m/%d")

    if doesFileExists(configuration):
        log.debug("Yaa I find the config")
        config = get_config_schema(configuration)
        write_weeknote(config, today)
    else:
        log.warning("Nope! Generating a new config")

        config = DEFAULT_CONFIG

    output_file = Path(configuration)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(output_file, "w") as f:
        json.dump(config, f)


if __name__ == "__main__":
    cli()
