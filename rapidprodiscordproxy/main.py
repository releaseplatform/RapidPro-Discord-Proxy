"""This module contains the main FastAPI logic as well as the startup logic for our application"""
import asyncio
import os
from typing import Dict
from uuid import UUID
from discord.flags import Intents

import uvicorn
from fastapi import FastAPI, HTTPException

import rapidprodiscordproxy.config
from rapidprodiscordproxy import RapidProMessage
from rapidprodiscordproxy.discord_handler import DiscordHandler

app = FastAPI()

channels: Dict[UUID, DiscordHandler] = {}

print("starting up")


@app.post("/discord/rp/send")
async def rapidpro_external_send(message: RapidProMessage):
    """This is our route for sending messages. If we pass in a valid
    RapidProMessage for a channel we know about, we forward the message to
    discord"""
    print(message)
    print(channels)
    if message.channel in channels:
        client: DiscordHandler = channels[message.channel]
    else:
        raise HTTPException(404, "No channel with that ID found")
    try:
        print(message)
        print(f"Attachments found in message: {message.attachments}")
        await client.send_dm(message)
    except client.UserNotFoundException:
        raise HTTPException(
            404,
            "No user with that ID found. Do they exist? Do you have permissions?",
        )


@app.on_event("startup")
async def startup():
    """Our initialization logic. We pull the config from the db and get a client
    for each discord channel configured in RapidPro"""
    if os.getenv("RP_DISCORD_PROXY_CONFIG_FILE") == "true":
        configs = rapidprodiscordproxy.config.parse_config_file("./config.toml")
    else:
        configs = rapidprodiscordproxy.config.get_configs_from_db()
    global channels
    for config in configs:
        print(config)
        intents = Intents.default()
        intents.members = True
        client = DiscordHandler(config, loop=asyncio.get_running_loop(), intents=intents)
        channels[config.channel_id] = client
        await client.login()
        asyncio.create_task(
            client.connect(),
            name=f"Discord Task {config.channel_id}",
        )
        await client.wait_for("ready")
        print("logged in successfully")


@app.on_event("shutdown")
async def shutdown():
    """This logs us out of all our clients so discord doesn't get angry at us."""
    for client in channels.values():
        await client.logout()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
