"""This module contains the DiscordHandler class, which handles our message logic"""
import io
import mimetypes
import os
import re
from typing import List, Union
from urllib.parse import urlparse

import discord
import emoji
import requests

from rapidprodiscordproxy import RapidProMessage
from rapidprodiscordproxy.config import RapidProDiscordConfig


class DiscordHandler(discord.Client):
    """This is our wrapper of the discord.Client which handles incoming
    messages, and can send messages we pass to it."""

    def __init__(self, config: RapidProDiscordConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

    async def on_ready(self):
        """This is called by the ready event once the client is logged on and
        initialized"""
        print(f"Successfully Logged on as {self.user}")

    async def on_message(self, message: discord.Message):
        """This is called by the message event whenever the bot sends/receives a
        message. We NOP when we send a message, or receive a message in a
        channel we're in without being @mentioned directly. We forward messages
        in which we've been mentioned to rapidpro, or any DMs"""
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

        attachments: List[str] = []
        if message.attachments:
            for attachment in message.attachments:
                attachments.append(attachment.url)
        requests.post(
            self.config.receive_url,
            data={"text": text, "from": message.author.id, "attachments": attachments},
        )
        print(
            "Forwarded to rapidpro"
            + repr(
                {"text": text, "from": message.author.id, "attachments": attachments}
            )
        )
        print("receive URL", self.config.receive_url)

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.user.id:
            return
        if payload.emoji.is_custom_emoji():
            found_emoji = f":{payload.emoji.name}:"
        else:
            found_emoji = str(payload.emoji)
        # print(f"Received reaction {emoji} on message from {payload.user_id}")
        requests.post(
            self.config.receive_url, data={"text": found_emoji, "from": payload.user_id}
        )

    async def send_msg(self, message: RapidProMessage):
        """This method allows us to send messages to users or channels, and will
        download any attachments from the URLs specified in the RapidProMessage
        that is passed as well."""
        user: discord.User = self.get_user(message.to)
        channel: discord.abc.Messageable = None
        if user is None:
            channel = self.get_channel(message.to)
            if channel is None:
                raise self.UserNotFoundException()
        elif user.dm_channel is None:
            await user.create_dm()
            channel = user.dm_channel

        if channel is not None and isinstance(channel, discord.abc.Messageable):
            if message.attachments is not None:
                for attachment in message.attachments:
                    req = requests.get(
                        attachment, stream=True, timeout=2
                    )  # TODO DO VERIFY
                    parsed = urlparse(attachment)
                    filename = os.path.basename(parsed.path)
                    print(f"resolved filename to {filename}")
                    content_type = req.headers.get("content-type")
                    print(content_type)
                    if filename == "":
                        filename = "Attached File"
                        if content_type is not None:
                            extension = mimetypes.guess_extension(content_type)
                            if extension is not None:
                                filename += extension
                    file = discord.File(io.BytesIO(req.raw.read()), filename=filename)
                    await channel.send(file=file)
            discord_msg: discord.Message = await channel.send(
                self.custom_emojiize(message.text)
            )

            for quick_reply in message.quick_replies:
                print(quick_reply)
                r = self.parse_quick_reply(quick_reply)
                if r != "":
                    await discord_msg.add_reaction(r)
            requests.post(self.config.sent_url, data={"id": message.id})

    async def login(self):
        await super().login(self.config.discord_bot_token)

    # async def send_channel(self, message: str, channel_id: int):
    #     channel: discord.TextChannel = self.get_channel(channel_id)
    #     if channel is not None and isinstance(channel, discord.TextChannel):
    #         await channel.send(message)
    #     else:
    #         raise self.ChannelNotFoundException()

    def parse_quick_reply(self, reply: str) -> Union[discord.Emoji, str]:
        """This finds out if we have a custom emoji that matches our quick
        reply. If it doesn't, we try to find an emoji that will work with the
        emoji library. If that fails, we can't parse it."""
        reply = reply.strip(":")
        print(self.emojis)
        for e in self.emojis:
            if e.name == reply:
                return e
        if emoji.emoji_count(reply) == 1:
            return reply
        return emoji.EMOJI_ALIAS_UNICODE.get(f":{reply}:", "")

    def custom_emojiize(self, message: str):
        """This finds custom emoji in a message by name, and replaces it with
        the way discord expects to see it."""
        pattern = re.compile(":[a-zA-Z0-9\\+\\-_&.ô’Åéãíç()!#*]+:")

        def repl(match: re.Match) -> str:
            for e in self.emojis:
                if e.name == match.group().strip(":"):
                    return str(e)
            return match.group()

        return pattern.sub(repl, message)

    class ChannelNotFoundException(Exception):
        pass

    class UserNotFoundException(Exception):
        pass
