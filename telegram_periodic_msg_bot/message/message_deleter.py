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

from typing import List

import pyrogram
import pyrogram.errors.exceptions as pyrogram_ex

from telegram_periodic_msg_bot.logger.logger import Logger


class MessageDeleter:
    """Class for deleting Telegram messages."""

    client: pyrogram.Client
    logger: Logger

    def __init__(self,
                 client: pyrogram.Client,
                 logger: Logger) -> None:
        """
        Initialize the message deleter.

        Args:
            client: Pyrogram client instance.
            logger: Logger instance for logging operations.
        """
        self.client = client
        self.logger = logger

    async def DeleteMessage(self,
                            message: pyrogram.types.Message) -> bool:
        """
        Delete a single message from a chat.

        Args:
            message: The message to delete.

        Returns:
            True if the message was successfully deleted, False otherwise.
        """
        try:
            if message.chat is not None:
                await self.client.delete_messages(message.chat.id, message.id)
                return True
        except pyrogram_ex.forbidden_403.MessageDeleteForbidden:
            self.logger.GetLogger().exception(f"Unable to delete message {message.id}")
        return False

    async def DeleteMessages(self,
                             messages: List[pyrogram.types.Message]) -> None:
        """
        Delete multiple messages from chats.

        Args:
            messages: List of messages to delete.
        """
        for message in messages:
            await self.DeleteMessage(message)
