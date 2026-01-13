import json
import logging
import os
import sys

from marshmallow import fields
from marshmallow import INCLUDE
from marshmallow import Schema
from marshmallow import ValidationError
from rich.logging import RichHandler

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


FORMAT = "%(message)s"
logging.basicConfig(
    level=LOG_LEVEL, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")


class LinkSchema(Schema):
    url = fields.URL(required=True)
    title = fields.Str(required=True)
    utm_source = fields.Str(load_default="fundor333.com")


class GoodreadSchema(Schema):
    user_id = fields.Str(required=True)
    shelf_name_code = fields.Str(required=True)
    shelf_name_label = fields.Str(required=True)


class GeneratorSchema(Schema):
    tag = fields.Str(load_default="week note")
    output = fields.Str(load_default="~/weeknotes/")
    fix_links_label = fields.Str(load_default="Fix Links")
    type_weeknote = fields.Str(load_default="weeknote")
    goodread = fields.Nested(GoodreadSchema, required=False)
    empty_section = fields.List(fields.Str, required=False)
    draft = fields.Bool(load_default=True)


class AnilistSchema(Schema):
    user_id = fields.Str(required=True)


class ConfigSchema(Schema):
    feeds = fields.List(fields.Nested(LinkSchema), required=True)
    fix_links = fields.List(fields.Nested(LinkSchema), required=True)
    generator = fields.Nested(GeneratorSchema, required=True)
    anilist = fields.Nested(AnilistSchema, required=False)
    goodread = fields.Nested(GoodreadSchema, required=False)
    empty_section = fields.List(fields.Str, required=False)

    class Meta:
        # Include unknown fields in the deserialized output
        unknown = INCLUDE


def get_config_schema(file_path: str) -> ConfigSchema:
    with open(file_path) as file:
        data = json.load(file)
    try:
        return ConfigSchema().load(data)
    except ValidationError as error:
        log.error(f"ERROR: {file_path} is invalid")
        log.error(error.messages)
        sys.exit(1)
