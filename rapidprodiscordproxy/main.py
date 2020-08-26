from fastapi import FastAPI, HTTPException
import uvicorn
from rapidprodiscordproxy import RapidProMessage
from rapidprodiscordproxy.discord_handler import DiscordHandler
import rapidprodiscordproxy.config
import asyncio
from typing import Dict
from uuid import UUID

app = FastAPI()

channels: Dict[UUID, DiscordHandler] = {}

print("starting up")


@app.post("/discord/rp/send")
async def rapidpro_external_send(message: RapidProMessage):
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
            404, "No user with that ID found. Do they exist? Do you have permissions?",
        )


@app.on_event("startup")
async def startup():
    # configs = rapidprodiscordproxy.config.parse_config_file("./config.toml")
    configs = rapidprodiscordproxy.config.get_configs_from_db()
    global channels
    for c in configs:
        print(c)
        client = DiscordHandler(c, loop=asyncio.get_running_loop())
        channels[c.channel_id] = client
        await client.login()
        asyncio.create_task(
            client.connect(), name=f"Discord Task {c.channel_id}",
        )
        await client.wait_for("ready")
        print("logged in successfully")


@app.on_event("shutdown")
async def shutdown():
    for c in channels.values():
        await c.logout()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
