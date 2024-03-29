# Copyright (c) 2021 Emanuele Bellocchia
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

#
# Imports
#
from typing import List, Optional

import pyrogram

from telegram_periodic_msg_bot.logger.logger import Logger
from telegram_periodic_msg_bot.message.message_deleter import MessageDeleter
from telegram_periodic_msg_bot.message.message_sender import MessageSender


#
# Classes
#

# Periodic message sender class
class PeriodicMsgSender:

    logger: Logger
    delete_last_sent_msg: bool
    last_sent_msgs: Optional[List[pyrogram.types.Message]]
    message_deleter: MessageDeleter
    message_sender: MessageSender

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 logger: Logger) -> None:
        self.logger = logger
        self.delete_last_sent_msg = True
        self.last_sent_msgs = None
        self.message_deleter = MessageDeleter(client, logger)
        self.message_sender = MessageSender(client, logger)

    # Set delete last sent message
    def DeleteLastSentMessage(self,
                              flag: bool) -> None:
        self.delete_last_sent_msg = flag

    # Send message
    def SendMessage(self,
                    chat: pyrogram.types.Chat,
                    msg: str) -> None:
        if self.delete_last_sent_msg:
            self.__DeleteLastSentMessage()

        self.last_sent_msgs = self.message_sender.SendMessage(chat, msg)

    # Delete last sent message
    def __DeleteLastSentMessage(self) -> None:
        if self.last_sent_msgs is not None:
            self.message_deleter.DeleteMessages(self.last_sent_msgs)

        self.last_sent_msgs = None
