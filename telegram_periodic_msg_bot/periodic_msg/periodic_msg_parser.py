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

import pyrogram

from telegram_periodic_msg_bot.bot.bot_config_types import BotConfigTypes
from telegram_periodic_msg_bot.config.config_object import ConfigObject


class PeriodicMsgParserInvalidError(Exception):
    """Exception raised when a message is invalid or malformed."""


class PeriodicMsgParserTooLongError(Exception):
    """Exception raised when a message exceeds the maximum allowed length."""


class PeriodicMsgParser:
    """Parser for extracting and validating periodic messages."""

    config: ConfigObject

    def __init__(self,
                 config: ConfigObject) -> None:
        """
        Initialize the message parser.

        Args:
            config: Configuration object containing message constraints
        """
        self.config = config

    def Parse(self,
              message: pyrogram.types.Message) -> str:
        """
        Parse and validate a periodic message.

        Args:
            message: The message to parse

        Returns:
            The extracted and validated message text

        Raises:
            PeriodicMsgParserInvalidError: If the message is invalid or empty
            PeriodicMsgParserTooLongError: If the message exceeds maximum length
        """
        if message.text is None:
            raise PeriodicMsgParserInvalidError()

        try:
            msg = message.text[message.text.index("\n"):].strip()

            if msg == "":
                raise PeriodicMsgParserInvalidError()
            if len(msg) > self.config.GetValue(BotConfigTypes.MESSAGE_MAX_LEN):
                raise PeriodicMsgParserTooLongError()

            return msg

        except ValueError as ex:
            raise PeriodicMsgParserInvalidError() from ex
