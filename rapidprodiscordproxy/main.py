from fastapi import FastAPI
import uvicorn
from discord_handler import DiscordHandler
import asyncio

app = FastAPI()

client: DiscordHandler


@app.get("/")
async def root():
    return {"message": "hello"}


@app.post("/sendtoawen")
async def send_to_awen(message: str):
    print(message)
    await client.send_to_awen(message)


@app.on_event("startup")
async def startup():
    global client
    client = DiscordHandler(loop=asyncio.get_running_loop())
    print("logging in")
    await client.login("<SECRET GOES HERE>"),
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
