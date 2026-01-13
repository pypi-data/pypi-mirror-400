import datetime
import logging
import os

import feedparser
from requests.models import PreparedRequest
from rich.logging import RichHandler

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


FORMAT = "%(message)s"
logging.basicConfig(
    level=LOG_LEVEL, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


def generate_feed_text(
    title: str, link: str, today: datetime, utm_source: str
) -> str:
    flag = False
    output = f"""## {title}\n"""
    log.debug(f"Checking {title} feed")
    for element_link in feedparser.parse(link).entries:
        log.debug(f"Checking {element_link.title}")
        log.debug(f"Checking {element_link.link}")
        log.debug(f"Checking {element_link.published_parsed}")
        if (
            today.date() - datetime.timedelta(days=7)
            < datetime.datetime(*element_link.published_parsed[:6]).date()
        ):

            req = PreparedRequest()
            url = element_link.link

            if utm_source == "" or utm_source is None:
                params = {}
            else:
                params = {"utm_source": utm_source}
            req.prepare_url(url, params)
            ll = req.url

            flag = True
            output += f"- [{element_link.title}]({ll})\n"

    if flag:
        return output
    else:
        return ""
