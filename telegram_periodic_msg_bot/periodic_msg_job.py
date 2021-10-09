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
import pyrogram
from threading import Lock
from telegram_periodic_msg_bot.config import Config
from telegram_periodic_msg_bot.helpers import ChatHelper
from telegram_periodic_msg_bot.logger import Logger
from telegram_periodic_msg_bot.periodic_msg_sender import PeriodicMsgSender


#
# Classes
#

# Periodic message job data class
class PeriodicMsgJobData:

    chat: pyrogram.types.Chat
    period_hours: int
    msg_id: str
    running: bool

    # Constructor
    def __init__(self,
                 chat: pyrogram.types.Chat,
                 period_hours: int,
                 msg_id: str) -> None:
        self.chat = chat
        self.period_hours = period_hours
        self.msg_id = msg_id
        self.running = True

    # Get chat
    def Chat(self) -> pyrogram.types.Chat:
        return self.chat

    # Get period hours
    def PeriodHours(self) -> int:
        return self.period_hours

    # Get message ID
    def MessageId(self) -> str:
        return self.msg_id

    # Set if running
    def SetRunning(self,
                   flag: bool) -> None:
        self.running = flag

    # Get if running
    def IsRunning(self) -> bool:
        return self.running


# Periodic message job class
class PeriodicMsgJob:

    data: PeriodicMsgJobData
    logger: Logger
    message: str
    message_lock: Lock
    message_sender: PeriodicMsgSender

    # Constructor
    def __init__(self,
                 client: pyrogram.Client,
                 config: Config,
                 logger: Logger,
                 data: PeriodicMsgJobData) -> None:
        self.data = data
        self.logger = logger
        self.message = ""
        self.message_lock = Lock()
        self.message_sender = PeriodicMsgSender(client, config, logger)

    # Get data
    def Data(self) -> PeriodicMsgJobData:
        return self.data

    # Set if running
    def SetRunning(self,
                   flag: bool) -> None:
        self.data.SetRunning(flag)

    # Set delete last sent message
    def DeleteLastSentMessage(self,
                              flag: bool) -> None:
        self.message_sender.DeleteLastSentMessage(flag)

    # Get message
    def GetMessage(self) -> str:
        return self.message

    # Set message
    def SetMessage(self,
                   message: str) -> None:
        # Prevent accidental modifications while job is executing
        with self.message_lock:
            self.message = message

    # Do job
    def DoJob(self,
              chat: pyrogram.types.Chat) -> None:
        self.logger.GetLogger().info(f"Periodic message job started in chat '{ChatHelper.GetTitleOrId(chat)}'")

        with self.message_lock:
            if self.message == "":
                self.logger.GetLogger().info("No message set, exiting...")
                return

            self.message_sender.SendMessage(chat, self.message)
