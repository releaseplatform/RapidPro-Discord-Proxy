from fastapi import FastAPI
import uvicorn
from discord_handler import DiscordHandler
import asyncio

app = FastAPI()

client: DiscordHandler

token: str

with open("./discord-creds-DO-NOT-COMMIT.txt", "r") as f:
    token = f.read().strip()

print(token)


@app.get("/")
async def root():
    return {"message": "hello"}


@app.post("/discord/direct/send/")
async def send_discord_DM(message: str, recipient_id: int):
    """
    Sends a message to a specified user in their DMs.
    Must have the permissions to send messages.
    recipient_id is the internal ID for the discord user.
    It can be found using the discord client with developer mode enabled,
    right clicking on the user
    """
    await client.send_dm(message, recipient_id)


@app.post("/discord/channel/send/")
async def send_discord_channel(message: str, channel_id: int):
    await client.send_channel(message, channel_id)


@app.on_event("startup")
async def startup():
    global client
    client = DiscordHandler(loop=asyncio.get_running_loop())
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
