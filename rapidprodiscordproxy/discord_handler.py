import discord
import requests
import json


class DiscordHandler(discord.Client):
    def __init__(self, *args, callback_URL="http://localhost:5000", **kwargs):
        super().__init__(*args, **kwargs)
        self.callback_URL = callback_URL

    async def on_ready(self):
        print(f"Successfully Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        if self.user == message.author:
            return  # We don't want to handle messages we've sent.
        # print(
        #     f"Message received from: {message.author}\n"
        #     f"guild: {message.guild}\n"
        #     f"channel: {message.channel}\n"
        #     f"content: {message.content}\n"
        # )
        requests.post(self.callback_URL, data=self.__message_to_json(message))

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

    def __message_to_json(self, message: discord.Message) -> str:
        dictionary = {
            "content": message.clean_content,
            "author": str(message.author),
            "authorid": message.author.id,
            "guild": str(message.guild),
            "guildid": message.guild.id if message.guild is not None else None,
            "channel": str(message.channel),
            "channelid": message.channel.id,
            "timestamp": str(message.created_at),
        }
        return json.dumps(dictionary)
