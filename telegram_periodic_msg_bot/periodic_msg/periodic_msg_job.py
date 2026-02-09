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

from telegram_periodic_msg_bot.logger.logger import Logger
from telegram_periodic_msg_bot.misc.helpers import ChatHelper
from telegram_periodic_msg_bot.periodic_msg.periodic_msg_sender import PeriodicMsgSender


class PeriodicMsgJobData:
    """Data container for a periodic message job."""

    chat: pyrogram.types.Chat
    topic_id: int
    period_hours: int
    start_hour: int
    msg_id: str
    running: bool

    def __init__(self,
                 chat: pyrogram.types.Chat,
                 topic_id: int,
                 period_hours: int,
                 start_hour: int,
                 msg_id: str) -> None:
        """
        Initialize the job data.

        Args:
            chat: The chat where the job runs.
            topic_id: The topic where the job runs.
            period_hours: Period in hours between message sends.
            start_hour: Starting hour for the job.
            msg_id: Unique identifier for the message.
        """
        self.chat = chat
        self.topic_id = topic_id
        self.period_hours = period_hours
        self.start_hour = start_hour
        self.msg_id = msg_id
        self.running = True

    def Chat(self) -> pyrogram.types.Chat:
        """
        Get the chat associated with this job.

        Returns:
            The chat object.
        """
        return self.chat

    def TopicId(self) -> int:
        """
        Get the topic associated with this job.

        Returns:
            The Telegram topic ID.
        """
        return self.topic_id

    def PeriodHours(self) -> int:
        """
        Get the period in hours.

        Returns:
            The period in hours.
        """
        return self.period_hours

    def StartHour(self) -> int:
        """
        Get the starting hour.

        Returns:
            The starting hour.
        """
        return self.start_hour

    def MessageId(self) -> str:
        """
        Get the message ID.

        Returns:
            The message ID.
        """
        return self.msg_id

    def SetRunning(self,
                   flag: bool) -> None:
        """
        Set the running state of the job.

        Args:
            flag: True to set job as running, False otherwise.
        """
        self.running = flag

    def IsRunning(self) -> bool:
        """
        Check if the job is running.

        Returns:
            True if the job is running, False otherwise
        """
        return self.running


class PeriodicMsgJob:
    """Periodic message job that sends messages at scheduled intervals."""

    data: PeriodicMsgJobData
    logger: Logger
    message: str
    message_sender: PeriodicMsgSender

    def __init__(self,
                 client: pyrogram.Client,
                 logger: Logger,
                 data: PeriodicMsgJobData) -> None:
        """
        Initialize the periodic message job.

        Args:
            client: Pyrogram client instance
            logger: Logger instance for logging operations
            data: Job data containing configuration
        """
        self.data = data
        self.logger = logger
        self.message = ""
        self.message_sender = PeriodicMsgSender(client, logger)

    def Data(self) -> PeriodicMsgJobData:
        """
        Get the job data.

        Returns:
            The job data object
        """
        return self.data

    def SetRunning(self,
                   flag: bool) -> None:
        """
        Set the running state of the job.

        Args:
            flag: True to set job as running, False otherwise.
        """
        self.data.SetRunning(flag)

    def DeleteLastSentMessage(self,
                              flag: bool) -> None:
        """
        Configure whether to delete the last sent message.

        Args:
            flag: True to delete last message before sending new one, False otherwise
        """
        self.message_sender.DeleteLastSentMessage(flag)

    def GetMessage(self) -> str:
        """
        Get the message to be sent.

        Returns:
            The message text
        """
        return self.message

    def SetMessage(self,
                   message: str) -> None:
        """
        Set the message to be sent periodically.

        Args:
            message: The message text to send
        """
        self.message = message

    async def DoJob(self,
                    chat: pyrogram.types.Chat,
                    topic_id: int) -> None:
        """
        Execute the job by sending the periodic message.

        Args:
            chat: The chat to send the message to
            topic_id: The topic to send the message to
        """
        self.logger.GetLogger().info(
            f"Periodic message job started in chat '{ChatHelper.GetTitleOrId(chat)}' ({topic_id})"
        )
        if self.message == "":
            self.logger.GetLogger().info("No message set, exiting...")
            return
        await self.message_sender.SendMessage(chat, topic_id, self.message)
