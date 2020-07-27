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
        user: discord.User = self.get_user(user_id)
        if user is None:
            raise self.UserNotFoundException()
        if user.dm_channel is None:
            await user.create_dm()
        if user.dm_channel is not None and isinstance(
            user.dm_channel, discord.DMChannel
        ):
            await user.dm_channel.send(message)

    async def send_channel(self, message: str, channel_id: int):
        channel: discord.TextChannel = self.get_channel(channel_id)
        if channel is not None and isinstance(channel, discord.TextChannel):
            await channel.send(message)
        else:
            raise self.ChannelNotFoundException()

    class ChannelNotFoundException(Exception):
        pass

    class UserNotFoundException(Exception):
        pass
