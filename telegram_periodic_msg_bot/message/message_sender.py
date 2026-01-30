# Copyright (c) 2026 Emanuele Bellocchia
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import asyncio
from typing import Any, List, Union

import pyrogram

from telegram_periodic_msg_bot.logger.logger import Logger


class MessageSenderConst:
    """Constants for message sender configuration."""

    MSG_MAX_LEN: int = 4096
    SEND_MSG_SLEEP_TIME_SEC: float = 0.1


class MessageSender:
    """Class for sending Telegram messages with automatic splitting for long messages."""

    client: pyrogram.Client
    logger: Logger

    def __init__(self,
                 client: pyrogram.Client,
                 logger: Logger) -> None:
        """
        Initialize the message sender.

        Args:
            client: Pyrogram client instance
            logger: Logger instance for logging operations
        """
        self.client = client
        self.logger = logger

    async def SendMessage(self,
                          receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                          topic_id: int,
                          msg: str,
                          **kwargs: Any) -> List[pyrogram.types.Message]:
        """
        Send a message to a chat or user, splitting it if necessary.

        Args:
            receiver: The chat or user to send the message to
            topic_id: Topic to send message to
            msg: The message text to send
            **kwargs: Additional keyword arguments passed to send_message

        Returns:
            List of sent message objects
        """
        self.logger.GetLogger().info(f"Sending message (length: {len(msg)}):\n{msg}")
        return await self.__SendSplitMessage(receiver, topic_id, self.__SplitMessage(msg), **kwargs)

    async def __SendSplitMessage(self,
                                 receiver: Union[pyrogram.types.Chat, pyrogram.types.User],
                                 topic_id: int,
                                 split_msg: List[str],
                                 **kwargs: Any) -> List[pyrogram.types.Message]:
        """
        Send multiple message parts to a receiver.

        Args:
            receiver: The chat or user to send the messages to
            topic_id: Topic to send messages to
            split_msg: List of message parts to send
            **kwargs: Additional keyword arguments passed to send_message

        Returns:
            List of sent message objects
        """
        sent_msgs = []

        for msg_part in split_msg:
            sent_msgs.append(await self.client.send_message(receiver.id, msg_part, message_thread_id=topic_id, **kwargs))
            await asyncio.sleep(MessageSenderConst.SEND_MSG_SLEEP_TIME_SEC)

        return sent_msgs

    def __SplitMessage(self,
                       msg: str) -> List[str]:
        """
        Split a long message into parts that fit within Telegram's message length limit.

        Attempts to split at newline characters when possible to maintain message formatting.

        Args:
            msg: The message to split

        Returns:
            List of message parts
        """
        msg_parts = []

        while len(msg) > 0:
            if len(msg) <= MessageSenderConst.MSG_MAX_LEN:
                msg_parts.append(msg)
                break

            curr_part = msg[:MessageSenderConst.MSG_MAX_LEN]
            idx = curr_part.rfind("\n")

            if idx != -1:
                msg_parts.append(curr_part[:idx])
                msg = msg[idx + 1:]
            else:
                msg_parts.append(curr_part)
                msg = msg[MessageSenderConst.MSG_MAX_LEN + 1:]

        self.logger.GetLogger().info(f"Message split into {len(msg_parts)} part(s)")

        return msg_parts
