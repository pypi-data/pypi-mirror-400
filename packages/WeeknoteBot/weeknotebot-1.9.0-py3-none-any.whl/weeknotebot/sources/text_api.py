from datetime import datetime
from datetime import timedelta

import requests


def generate_tex_api(link: str) -> str:

    output = ""
    r = requests.get(link)
    for e in r.json():
        if (
            datetime.fromisoformat(e["created_at"]).date() + timedelta(days=7)
            > datetime.today().date()
        ):
            line = e["content"]
            line = line.replace("\n", " ")
            line = line.replace("\r", " ")
            line = line.replace("  ", " ")
            output += f"- {line}\n"
    output += "\n"
    return output
