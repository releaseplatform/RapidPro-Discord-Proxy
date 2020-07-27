import discord


class DiscordHandler(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"Successfully Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        if self.user == message.author:
            return  # We don't want to handle messages we've sent.
        print(
            f"Message received from: {message.author}\n"
            f"guild: {message.guild}\n"
            f"channel: {message.channel}\n"
            f"content: {message.content}\n"
        )

    async def send_dm(self, message: str, user_id: int):
        # channel: discord.TextChannel = self.get_channel(737097898738581599)
        # await channel.send(message)
        user: discord.User = self.get_user(user_id)
        if user.dm_channel is None:
            await user.create_dm()
        await user.dm_channel.send(message)

    async def send_channel(self, message: str, channel_id: int):
        channel: discord.GroupChannel = self.get_channel(channel_id)
        await channel.send(message)
