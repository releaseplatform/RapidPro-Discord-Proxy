from pydantic import BaseModel, AnyHttpUrl
import uuid
import toml
from typing import List


class RapidProDiscordConfig(BaseModel):
    rapidpro_domain: AnyHttpUrl
    channel_id: uuid.UUID
    discord_bot_token: str
    name: str

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
