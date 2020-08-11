import discord
import requests
from rapidprodiscordproxy import RapidProMessage
from rapidprodiscordproxy.config import RapidProDiscordConfig
import re


class DiscordHandler(discord.Client):
    def __init__(self, config: RapidProDiscordConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    async def on_ready(self):
        print(f"Successfully Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        if self.user == message.author:
            return  # We don't want to handle messages we've sent.

        if isinstance(message.channel, discord.DMChannel):
            # This is when we receive a DM from a user
            print(f"We received a message from {message.author}: {message.content}")
            text = message.clean_content
        elif self.user.mentioned_in(message) and not message.mention_everyone:
            # If someone's in a channel that contains the bot, and @mentions the bot
            text = re.sub(
                r"<@!?" + str(self.user.id) + r">\s", "", message.content
            )  # strip the mention
            print(
                "Bot was directly mentioned in a channel by "
                f"{message.author}: {message.clean_content}"
            )
        else:
            # We don't want the entire chat history of the channel in RP, only bot stuff
            print("ordinary channel message -- ignoring")
            return
        print(f"id: {message.author.id}, usernameanddiscriminator: {message.author}")
        author_with_fragment = f"{message.author.id}#{message.author}"
        print(author_with_fragment)

        requests.post(
            self.config.receive_url, data={"text": text, "from": message.author.id}
        )
        print("Forwarded to rapidpro" + repr({"text": text, "from": message.author.id}))
        print("receive URL", self.config.receive_url)

    async def send_dm(self, message: RapidProMessage):
        user: discord.User = self.get_user(message.to)
        if user is None:
            raise self.UserNotFoundException()
        if user.dm_channel is None:
            await user.create_dm()
        if user.dm_channel is not None and isinstance(
            user.dm_channel, discord.DMChannel
        ):
            await user.dm_channel.send(message.text)
            requests.post(self.config.sent_url, data={"id": message.id})

    async def login(self):
        await super().login(self.config.discord_bot_token)

    # async def send_channel(self, message: str, channel_id: int):
    #     channel: discord.TextChannel = self.get_channel(channel_id)
    #     if channel is not None and isinstance(channel, discord.TextChannel):
    #         await channel.send(message)
    #     else:
    #         raise self.ChannelNotFoundException()

    class ChannelNotFoundException(Exception):
        pass

    class UserNotFoundException(Exception):
        pass
