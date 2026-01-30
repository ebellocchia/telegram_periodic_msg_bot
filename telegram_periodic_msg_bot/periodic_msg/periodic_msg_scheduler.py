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

from typing import Dict

import pyrogram
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from telegram_periodic_msg_bot.bot.bot_config_types import BotConfigTypes
from telegram_periodic_msg_bot.config.config_object import ConfigObject
from telegram_periodic_msg_bot.logger.logger import Logger
from telegram_periodic_msg_bot.misc.helpers import ChatHelper
from telegram_periodic_msg_bot.periodic_msg.periodic_msg_job import PeriodicMsgJob, PeriodicMsgJobData
from telegram_periodic_msg_bot.periodic_msg.periodic_msg_parser import PeriodicMsgParser
from telegram_periodic_msg_bot.translator.translation_loader import TranslationLoader
from telegram_periodic_msg_bot.utils.wrapped_list import WrappedList


class PeriodicMsgJobAlreadyExistentError(Exception):
    """Exception raised when attempting to create a job that already exists."""


class PeriodicMsgJobNotExistentError(Exception):
    """Exception raised when attempting to operate on a non-existent job."""


class PeriodicMsgJobInvalidPeriodError(Exception):
    """Exception raised when the job period is outside valid range."""


class PeriodicMsgJobInvalidStartError(Exception):
    """Exception raised when the job start hour is outside valid range."""


class PeriodicMsgJobMaxNumError(Exception):
    """Exception raised when the maximum number of jobs is reached."""


class PeriodicMsgSchedulerConst:
    """Constants for periodic message scheduler configuration."""

    MIN_START_HOUR: int = 0
    MAX_START_HOUR: int = 23
    MIN_PERIOD_HOURS: int = 1
    MAX_PERIOD_HOURS: int = 24


class PeriodicMsgJobsList(WrappedList):
    """List of periodic message jobs with formatted string output."""

    translator: TranslationLoader

    def __init__(self,
                 translator: TranslationLoader) -> None:
        """
        Initialize the jobs list.

        Args:
            translator: Translation loader for localized messages
        """
        super().__init__()
        self.translator = translator

    def ToString(self) -> str:
        """
        Convert the jobs list to a formatted string.

        Returns:
            A newline-separated list of job information
        """
        return "\n".join(
            [self.translator.GetSentence("SINGLE_TASK_INFO_MSG",
                                         msg_id=job_data.MessageId(),
                                         topic_id=job_data.TopicId(),
                                         period=job_data.PeriodHours(),
                                         start=job_data.StartHour(),
                                         state=(self.translator.GetSentence("TASK_RUNNING_MSG")
                                                if job_data.IsRunning()
                                                else self.translator.GetSentence("TASK_PAUSED_MSG"))
                                         )
             for job_data in self.list_elements]
        )

    def __str__(self) -> str:
        """
        Convert the jobs list to a string.

        Returns:
            A newline-separated list of job information
        """
        return self.ToString()


class PeriodicMsgScheduler:
    """Scheduler for managing periodic message jobs across multiple chats."""

    client: pyrogram.Client
    config: ConfigObject
    logger: Logger
    translator: TranslationLoader
    jobs: Dict[str, PeriodicMsgJob]
    scheduler: AsyncIOScheduler

    def __init__(self,
                 client: pyrogram.Client,
                 config: ConfigObject,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        """
        Initialize the periodic message scheduler.

        Args:
            client: Pyrogram client instance
            config: Configuration object
            logger: Logger instance for logging operations
            translator: Translation loader for localized messages
        """
        self.client = client
        self.config = config
        self.logger = logger
        self.translator = translator
        self.jobs = {}
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    def GetJobsInChat(self,
                      chat: pyrogram.types.Chat) -> PeriodicMsgJobsList:
        """
        Get the list of active jobs in a chat.

        Args:
            chat: The chat to get jobs for

        Returns:
            List of active jobs in the chat
        """
        chat_id_str = str(chat.id)

        jobs_list = PeriodicMsgJobsList(self.translator)
        jobs_list.AddMultiple([job.Data() for (job_id, job) in self.jobs.items() if job_id.startswith(chat_id_str)])

        return jobs_list

    def IsActiveInChat(self,
                       chat: pyrogram.types.Chat,
                       topic_id: int,
                       msg_id: str) -> bool:
        """
        Check if a job is active in a chat.

        Args:
            chat: The chat to check
            topic_id: The topic to check
            msg_id: The message ID of the job

        Returns:
            True if the job is active, False otherwise
        """
        job_id = self.__GetJobId(chat, topic_id, msg_id)
        return job_id in self.jobs and self.scheduler.get_job(job_id) is not None

    def Start(self,
              chat: pyrogram.types.Chat,
              topic_id: int,
              period_hours: int,
              start_hour: int,
              msg_id: str,
              message: pyrogram.types.Message) -> None:
        """
        Start a new periodic message job.

        Args:
            chat: The chat to start the job in
            topic_id: The topic to start the job in
            period_hours: Period in hours between messages
            start_hour: Starting hour for the job
            msg_id: Unique identifier for the message
            message: The message to send periodically

        Raises:
            PeriodicMsgJobAlreadyExistentError: If job already exists
            PeriodicMsgJobInvalidPeriodError: If period is invalid
            PeriodicMsgJobInvalidStartError: If start hour is invalid
            PeriodicMsgJobMaxNumError: If maximum number of jobs reached
        """
        job_id = self.__GetJobId(chat, topic_id, msg_id)

        if self.IsActiveInChat(chat, topic_id, msg_id):
            self.logger.GetLogger().error(
                f"Job '{job_id}' already active in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}), cannot start it"
            )
            raise PeriodicMsgJobAlreadyExistentError()

        if period_hours < PeriodicMsgSchedulerConst.MIN_PERIOD_HOURS or period_hours > PeriodicMsgSchedulerConst.MAX_PERIOD_HOURS:
            self.logger.GetLogger().error(
                f"Invalid period {period_hours} for job '{job_id}', cannot start it"
            )
            raise PeriodicMsgJobInvalidPeriodError()

        if start_hour < PeriodicMsgSchedulerConst.MIN_START_HOUR or start_hour > PeriodicMsgSchedulerConst.MAX_START_HOUR:
            self.logger.GetLogger().error(
                f"Invalid start hour {start_hour} for job '{job_id}', cannot start it"
            )
            raise PeriodicMsgJobInvalidStartError()

        tot_job_cnt = self.__GetTotalJobCount()
        if tot_job_cnt >= self.config.GetValue(BotConfigTypes.TASKS_MAX_NUM):
            self.logger.GetLogger().error("Maximum number of jobs reached, cannot start a new one")
            raise PeriodicMsgJobMaxNumError()

        self.__CreateJob(job_id, chat, topic_id, period_hours, start_hour, msg_id, message)
        self.__AddJob(job_id, chat, topic_id, period_hours, start_hour, msg_id)

    def GetMessage(self,
                   chat: pyrogram.types.Chat,
                   topic_id: int,
                   msg_id: str) -> str:
        """
        Get the message for a job.

        Args:
            chat: The chat containing the job
            topic_id: The topic containing the job
            msg_id: The message ID of the job

        Returns:
            The job's message text

        Raises:
            PeriodicMsgJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, topic_id, msg_id)

        if not self.IsActiveInChat(chat, topic_id, msg_id):
            self.logger.GetLogger().error(
                f"Job '{job_id}' not active in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}), cannot get message"
            )
            raise PeriodicMsgJobNotExistentError()

        return self.jobs[job_id].GetMessage()

    def SetMessage(self,
                   chat: pyrogram.types.Chat,
                   topic_id: int,
                   msg_id: str,
                   message: pyrogram.types.Message) -> None:
        """
        Set the message for a job.

        Args:
            chat: The chat containing the job
            topic_id: The topic containing the job
            msg_id: The message ID of the job
            message: The new message to set

        Raises:
            PeriodicMsgJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, topic_id, msg_id)

        if not self.IsActiveInChat(chat, topic_id, msg_id):
            self.logger.GetLogger().error(
                f"Job '{job_id}' not active in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}), cannot set message"
            )
            raise PeriodicMsgJobNotExistentError()

        msg = PeriodicMsgParser(self.config).Parse(message)

        self.jobs[job_id].SetMessage(msg)
        self.logger.GetLogger().info(
            f"Set message to job '{job_id}' in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}): {msg}"
        )

    def Stop(self,
             chat: pyrogram.types.Chat,
             topic_id: int,
             msg_id: str) -> None:
        """
        Stop a periodic message job.

        Args:
            chat: The chat containing the job
            topic_id: The topic containing the job
            msg_id: The message ID of the job

        Raises:
            PeriodicMsgJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, topic_id, msg_id)

        if not self.IsActiveInChat(chat, topic_id, msg_id):
            self.logger.GetLogger().error(
                f"Job '{job_id}' not active in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}), cannot stop it"
            )
            raise PeriodicMsgJobNotExistentError()

        self.scheduler.remove_job(job_id)
        self.jobs.pop(job_id, None)

        self.logger.GetLogger().info(
            f"Stopped job '{job_id}' in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}), "
            f"number of active jobs: {self.__GetTotalJobCount()}"
        )

    def StopAll(self,
                chat: pyrogram.types.Chat) -> None:
        """
        Stop all jobs in a chat.

        Args:
            chat: The chat to stop all jobs in
        """
        chat_id_str = str(chat.id)
        job_ids = [job_id for job_id in self.jobs.keys() if job_id.startswith(chat_id_str)]
        if len(job_ids) == 0:
            self.logger.GetLogger().info(
                f"No job to stop in chat {ChatHelper.GetTitleOrId(chat)}, exiting..."
            )
            return

        for job_id in job_ids:
            self.scheduler.remove_job(job_id)
            self.jobs.pop(job_id, None)
            self.logger.GetLogger().info(
                f"Stopped job '{job_id}' in chat {ChatHelper.GetTitleOrId(chat)}"
            )
        self.logger.GetLogger().info(
            f"Removed all jobs in chat {ChatHelper.GetTitleOrId(chat)}, number of active jobs: {self.__GetTotalJobCount()}"
        )

    def ChatLeft(self,
                 chat: pyrogram.types.Chat) -> None:
        """
        Handle bot leaving a chat by stopping all jobs.

        Args:
            chat: The chat that was left
        """
        self.logger.GetLogger().info(
            f"Left chat {ChatHelper.GetTitleOrId(chat)}, stopping all jobs..."
        )
        self.StopAll(chat)

    def Pause(self,
              chat: pyrogram.types.Chat,
              topic_id: int,
              msg_id: str) -> None:
        """
        Pause a periodic message job.

        Args:
            chat: The chat containing the job
            topic_id: The topic containing the job
            msg_id: The message ID of the job

        Raises:
            PeriodicMsgJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, topic_id, msg_id)

        if not self.IsActiveInChat(chat, topic_id, msg_id):
            self.logger.GetLogger().error(
                f"Job '{job_id}' not active in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}), cannot pause it"
            )
            raise PeriodicMsgJobNotExistentError()

        self.jobs[job_id].SetRunning(False)
        self.scheduler.pause_job(job_id)
        self.logger.GetLogger().info(f"Paused job '{job_id}' in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id})")

    def Resume(self,
               chat: pyrogram.types.Chat,
               topic_id: int,
               msg_id: str) -> None:
        """
        Resume a paused periodic message job.

        Args:
            chat: The chat containing the job
            topic_id: The topic containing the job
            msg_id: The message ID of the job

        Raises:
            PeriodicMsgJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, topic_id, msg_id)

        if not self.IsActiveInChat(chat, topic_id, msg_id):
            self.logger.GetLogger().error(
                f"Job '{job_id}' not active in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}), cannot resume it"
            )
            raise PeriodicMsgJobNotExistentError()

        self.jobs[job_id].SetRunning(True)
        self.scheduler.resume_job(job_id)
        self.logger.GetLogger().info(f"Resumed job '{job_id}' in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id})")

    def DeleteLastSentMessage(self,
                              chat: pyrogram.types.Chat,
                              topic_id: int,
                              msg_id: str,
                              flag: bool) -> None:
        """
        Configure whether to delete the last sent message for a job.

        Args:
            chat: The chat containing the job
            topic_id: The topic containing the job
            msg_id: The message ID of the job
            flag: True to delete last message, False to keep it

        Raises:
            PeriodicMsgJobNotExistentError: If job does not exist
        """
        job_id = self.__GetJobId(chat, topic_id, msg_id)

        if not self.IsActiveInChat(chat, topic_id, msg_id):
            self.logger.GetLogger().error(
                f"Job '{job_id}' not active in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id})"
            )
            raise PeriodicMsgJobNotExistentError()

        self.jobs[job_id].DeleteLastSentMessage(flag)
        self.logger.GetLogger().info(
            f"Set delete last message to {flag} for job '{job_id}' in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id})"
        )

    def __CreateJob(self,
                    job_id: str,
                    chat: pyrogram.types.Chat,
                    topic_id: int,
                    period: int,
                    start: int,
                    msg_id: str,
                    message: pyrogram.types.Message) -> None:
        """
        Create a new job instance and store it.

        Args:
            job_id: Unique job identifier
            chat: The chat for the job
            topic_id: The topic for the job
            period: Period in hours
            start: Starting hour
            msg_id: Message identifier
            message: The message to send
        """
        msg = PeriodicMsgParser(self.config).Parse(message)
        self.jobs[job_id] = PeriodicMsgJob(self.client,
                                           self.logger,
                                           PeriodicMsgJobData(chat, topic_id, period, start, msg_id))
        self.jobs[job_id].SetMessage(msg)

    def __AddJob(self,
                 job_id: str,
                 chat: pyrogram.types.Chat,
                 topic_id: int,
                 period: int,
                 start: int,
                 msg_id: str) -> None:
        """
        Add a job to the scheduler with cron configuration.

        Args:
            job_id: Unique job identifier
            chat: The chat for the job
            topic_id: The topic for the job
            period: Period in hours
            start: Starting hour
            msg_id: Message identifier
        """
        is_test_mode = self.config.GetValue(BotConfigTypes.APP_TEST_MODE)
        cron_str = self.__BuildCronString(period, start, is_test_mode)
        if is_test_mode:
            self.scheduler.add_job(self.jobs[job_id].DoJob,
                                   "cron",
                                   args=(chat,topic_id,),
                                   minute=cron_str,
                                   id=job_id)
        else:
            self.scheduler.add_job(self.jobs[job_id].DoJob,
                                   "cron",
                                   args=(chat,topic_id,),
                                   hour=cron_str,
                                   id=job_id)
        per_sym = "minute(s)" if is_test_mode else "hour(s)"
        self.logger.GetLogger().info(
            f"Started job '{job_id}' in chat {ChatHelper.GetTitleOrId(chat)} ({topic_id}) ({period} {per_sym}, "
            f"{msg_id}), number of active jobs: {self.__GetTotalJobCount()}, cron: {cron_str}"
        )

    @staticmethod
    def __GetJobId(chat: pyrogram.types.Chat,
                   topic_id: int,
                   msg_id: str) -> str:
        """
        Generate a unique job ID from chat and message IDs.

        Args:
            chat: The chat
            topic_id: The topic
            msg_id: The message ID

        Returns:
            The generated job ID
        """
        return f"{chat.id}-{topic_id}-{msg_id}"

    def __GetTotalJobCount(self) -> int:
        """
        Get the total number of active jobs across all chats.

        Returns:
            Total number of active jobs
        """
        return len(self.jobs)

    @staticmethod
    def __BuildCronString(period: int,
                          start_val: int,
                          is_test_mode: bool) -> str:
        """
        Build a cron string for the job schedule.

        Args:
            period: Period between executions
            start_val: Starting value
            is_test_mode: True for minute-based testing, False for hour-based

        Returns:
            Comma-separated cron schedule string
        """
        max_val = 24 if not is_test_mode else 60

        cron_str = ""

        loop_cnt = max_val // period
        if max_val % period != 0:
            loop_cnt += 1

        t = start_val
        for _ in range(loop_cnt):
            cron_str += f"{t},"
            t = (t + period) % max_val

        return cron_str[:-1]
