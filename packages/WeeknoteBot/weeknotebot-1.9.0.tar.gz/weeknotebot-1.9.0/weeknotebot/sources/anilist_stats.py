import logging
import os

import requests
from rich.logging import RichHandler

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


FORMAT = "%(message)s"
logging.basicConfig(
    level=LOG_LEVEL, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


def get_query_anime_stats(user_id: str) -> str:
    return (
        """{
  User(name: \""""
        + user_id
        + """\"
) {
id
    name
    about
    statistics {
      anime {
        count
        minutesWatched
        episodesWatched
        genres(limit: 5) {
          genre
        }
      }
      manga {
        count
        chaptersRead
        volumesRead
        genres(limit: 5) {
          genre
        }
      }
    }
  }
}"""
    )


def from_minute_to_hour(minute: int) -> str:
    return str(minute // 60) + "h " + str(minute % 60) + "m"


def get_anilist_row(user_id: str) -> str:

    req = requests.post(
        "https://graphql.anilist.co",
        json={"query": get_query_anime_stats(user_id=user_id)},
    )

    data = req.json()

    stats = data["data"]["User"]["statistics"]
    anime = stats["anime"]
    manga = stats["manga"]

    anime_count = anime["count"]
    anime_hours = from_minute_to_hour(anime["minutesWatched"])
    anime_episodes = anime["episodesWatched"]
    anime_genres = ["🏷️ " + genre["genre"] for genre in anime["genres"]]

    manga_count = manga["count"]
    manga_chapters = manga["chaptersRead"]
    manga_volumes = manga["volumesRead"]
    manga_genres = ["🏷️ " + genre["genre"] for genre in manga["genres"]]

    output = "\n## Anime and manga's stats\n"
    output += "\n### **Anime**\n"
    output += f"- Total anime watched: **{anime_count}**\n"
    output += f"- Total anime watched time: **{anime_hours}**\n"
    output += f"- Total anime watched episodes: **{anime_episodes}**\n"
    output += f"- Top 5 anime genres: {', '.join(anime_genres)}\n"
    output += "\n### **Manga**\n"
    output += f"- Total manga read: **{manga_count}**\n"
    output += f"- Total manga read chapters: **{manga_chapters}**\n"
    output += f"- Total manga read volumes: **{manga_volumes}**\n"
    output += f"- Top 5 manga genres: {', '.join(manga_genres)}\n"

    return output
