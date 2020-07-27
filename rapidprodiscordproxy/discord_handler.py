import discord


class DiscordHandler(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"Successfully Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        if self.user == message.author:
            return  # We don't want to handle messages we've sent.
        print(f"Message received from {message.author}: {message.content}")

    async def send_to_awen(self, message: str):
        # channel: discord.TextChannel = self.get_channel(737097898738581599)
        # await channel.send(message)
        user: discord.User = self.get_user(694634743521607802)
        if user.dm_channel is None:
            await user.create_dm()
        await user.dm_channel.send(message)

