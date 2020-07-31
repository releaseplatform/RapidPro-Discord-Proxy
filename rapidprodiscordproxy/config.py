from pydantic import BaseModel, AnyHttpUrl
import uuid
import toml
from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import codegen.models
import json

DATABASE_URL = "postgresql://temba:temba@192.168.122.207"
RAPIDPRO_DOMAIN = "http://localhost"

CHANNEL_TYPE = "EX"  # This will later be something specific to discord

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    This is a dependency (in the FastAPI sense) that can give us a DB session
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RapidProDiscordConfig(BaseModel):
    rapidpro_domain: AnyHttpUrl
    channel_id: uuid.UUID
    discord_bot_token: str
    name: Optional[str]

    @property
    def base_url(self):
        return str(self.rapidpro_domain) + "/c/ex/" + str(self.channel_id)

    @property
    def receive_url(self):
        return self.base_url + "/receive"

    @property
    def sent_url(self):
        return self.base_url + "/sent"

    @property
    def failed_url(self):
        return self.base_url + "/failed"

    # class Config:
    #     orm_mode = True


def parse_config_file(path: str) -> List[RapidProDiscordConfig]:
    try:
        with open("./config.toml", "r") as file:
            configs: List[RapidProDiscordConfig] = []
            raw_config = toml.load(file)
            for c in raw_config["config"]:
                configs.append(RapidProDiscordConfig(**c))
            return configs
    except Exception as e:
        print("Error loading config file:", str(e))
        raise e


parse_config_file("./config.toml")


def get_configs_from_db() -> List[RapidProDiscordConfig]:
    """
    This fetches the channel configs from the RapidPro db, and returns our configs
    """
    db = SessionLocal()
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
