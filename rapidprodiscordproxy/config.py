"""This module encapsulates the configuration logic for our application."""
import json
import os
import uuid
from typing import List, Optional

import toml
from pydantic import AnyHttpUrl, BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import codegen.models

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://temba:temba@localhost")
RAPIDPRO_DOMAIN = os.getenv("RAPIDPRO_DOMAIN", "http://localhost")

CHANNEL_TYPE = "DS"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class RapidProDiscordConfig(BaseModel):
    """This pydantic model represents the config variables that we need. It can
    either be populated straight from the rapidpro database, or from a separate
    file"""

    rapidpro_domain: AnyHttpUrl
    channel_id: uuid.UUID
    discord_bot_token: str
    name: Optional[str]
    roles_base_url: Optional[AnyHttpUrl]

    @property
    def base_url(self):
        """The base URL for the courier instance we want to talk to. It is of
        the form http(s)://domain.tld/c/ds/<UUID>"""
        return str(self.rapidpro_domain) + "/c/ds/" + str(self.channel_id)

    @property
    def receive_url(self):
        """The receive URL configured in courier. This is where we send messages."""
        return self.base_url + "/receive"

    @property
    def sent_url(self):
        """The sent URL configured in courier. This is where we inform courier
        when we've successfully sent a message."""
        return self.base_url + "/sent"

    @property
    def failed_url(self):
        """The failed URL configured in courier. This is where we inform courier
        when we've been unable to send a message."""
        return self.base_url + "/failed"

    @property
    def roles_update_url(self):
        if self.roles_base_url is not None:
            return self.roles_base_url + "/update"
        else:
            return None


def parse_config_file(path: str = "./config.yml") -> List[RapidProDiscordConfig]:
    """This parses a config file. This method isn't used normally, but is
    included in the situation where we don't want to give direct access to the
    postgres instance that rapidpro is using."""
    try:
        with open(path, "r") as file:
            configs: List[RapidProDiscordConfig] = []
            raw_config = toml.load(file)
            for config in raw_config["config"]:
                configs.append(RapidProDiscordConfig(**config))
            return configs
    except Exception as e:
        print("Error loading config file:", str(e))
        raise e


def get_configs_from_db() -> List[RapidProDiscordConfig]:
    """
    This fetches the channel configs from the RapidPro db, and returns our configs
    """
    db: Session = SessionLocal()
    channels = (
        db.query(codegen.models.ChannelsChannel)
        .filter(
            codegen.models.ChannelsChannel.channel_type == CHANNEL_TYPE,
            codegen.models.ChannelsChannel.is_active,
        )
        .all()
    )
    configs: List[RapidProDiscordConfig] = []
    for channel in channels:
        channel_raw_config = json.loads(channel.config)
        configs.append(
            RapidProDiscordConfig(
                rapidpro_domain=RAPIDPRO_DOMAIN,
                channel_id=channel.uuid,
                name=channel.name,
                discord_bot_token=channel_raw_config["auth_token"],
            )
        )
    return configs
