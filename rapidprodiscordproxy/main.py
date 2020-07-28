from fastapi import FastAPI, HTTPException
import uvicorn
from discord_handler import DiscordHandler
import asyncio

app = FastAPI()

client: DiscordHandler

token: str

with open("./discord-creds-DO-NOT-COMMIT.txt", "r") as f:
    token = f.read().strip()

print(token)


@app.post("/discord/direct/send/")
async def send_discord_DM(message: str, recipient_id: int):
    """
    Sends a message to a specified user in their DMs.
    Must have the permissions to send messages.
    recipient_id is the internal ID for the discord user.
    It can be found using the discord client with developer mode enabled,
    right clicking on the user
    """
    try:
        await client.send_dm(message, recipient_id)
    except client.UserNotFoundException:
        raise HTTPException(
            404, "No user with that ID found. Do they exist? Do you have permissions?",
        )


@app.post("/discord/channel/send/")
async def send_discord_channel(message: str, channel_id: int):
    try:
        await client.send_channel(message, channel_id)
    except DiscordHandler.ChannelNotFoundException:
        raise HTTPException(
            404, "Could not find a discord channel with that ID. Does it exist?"
        )


@app.post("/discord/rp/send")
async def rapidpro_external_send(text: str, to: int, _from: int, channel: int, id: int):
    print(text, to, _from, channel, id)


@app.on_event("startup")
async def startup():
    global client
    client = DiscordHandler(
        loop=asyncio.get_running_loop(),
        callback_URL="http://localhost:8080/c/ex/a94f98ef-99f9-4fc3-b4db-479bdff4bbe8/receive",
    )
    print("logging in")
    await client.login(token),
    asyncio.create_task(
        client.connect(), name="Discord Task",
    )
    await client.wait_for("ready")
    print("logged in successfully")


@app.on_event("shutdown")
async def shutdown():
    await client.logout()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
