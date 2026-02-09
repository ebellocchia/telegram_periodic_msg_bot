# Copyright (c) 2026-2026 Emanuele Bellocchia
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

from typing import Any, Callable, Coroutine

from typing_extensions import override

from telegram_periodic_msg_bot._version import __version__
from telegram_periodic_msg_bot.bot.bot_config_types import BotConfigTypes
from telegram_periodic_msg_bot.command.command_base import CommandBase
from telegram_periodic_msg_bot.command.command_data import CommandParameterError
from telegram_periodic_msg_bot.misc.helpers import UserHelper
from telegram_periodic_msg_bot.periodic_msg.periodic_msg_parser import PeriodicMsgParserInvalidError, PeriodicMsgParserTooLongError
from telegram_periodic_msg_bot.periodic_msg.periodic_msg_scheduler import (
    PeriodicMsgJobAlreadyExistentError,
    PeriodicMsgJobInvalidPeriodError,
    PeriodicMsgJobInvalidStartError,
    PeriodicMsgJobMaxNumError,
    PeriodicMsgJobNotExistentError,
)


def GroupChatOnly(exec_cmd_fct: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """
    Decorator for group-only commands.

    Args:
        exec_cmd_fct: Command execution function.

    Returns:
        Decorated function that checks for group chat.
    """
    async def decorated(self, **kwargs: Any):
        if self._IsPrivateChat():
            await self._SendMessage(self.translator.GetSentence("GROUP_ONLY_ERR_MSG"))
        else:
            await exec_cmd_fct(self, **kwargs)

    return decorated


class HelpCmd(CommandBase):
    """Command for displaying help information."""

    @override
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the help command."""
        await self._SendMessage(
            self.translator.GetSentence(
                "HELP_CMD",
                name=UserHelper.GetName(self.cmd_data.User()),
            ),
        )


class AliveCmd(CommandBase):
    """Command for checking if the bot is alive."""

    @override
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the alive command."""
        await self._SendMessage(self.translator.GetSentence("ALIVE_CMD"))


class SetTestModeCmd(CommandBase):
    """Command for setting test mode."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the set test mode command."""
        try:
            flag = self.cmd_data.Params().GetAsBool(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            self.config.SetValue(BotConfigTypes.APP_TEST_MODE, flag)

            if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
                await self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_EN_CMD"))
            else:
                await self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_DIS_CMD"))


class IsTestModeCmd(CommandBase):
    """Command for checking if test mode is enabled."""

    @override
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the is test mode command."""
        if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            await self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_EN_CMD"))
        else:
            await self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_DIS_CMD"))


class VersionCmd(CommandBase):
    """Command for showing the bot version."""

    @override
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the version command."""
        await self._SendMessage(
            self.translator.GetSentence(
                "VERSION_CMD",
                version=__version__,
            ),
        )


class MessageTaskStartCmd(CommandBase):
    """Command for starting a periodic message task."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task start command."""
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
            period_hours = self.cmd_data.Params().GetAsInt(1)
            start_hour = self.cmd_data.Params().GetAsInt(2, 0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].Start(
                    self.cmd_data.Chat(),
                    self.message.message_thread_id,
                    period_hours,
                    start_hour,
                    msg_id,
                    self.message,
                )
                await self._SendMessage(
                    self.translator.GetSentence(
                        "MESSAGE_TASK_START_OK_CMD",
                        period=period_hours,
                        start=start_hour,
                        msg_id=msg_id,
                    ),
                )
            except PeriodicMsgJobInvalidPeriodError:
                await self._SendMessage(self.translator.GetSentence("TASK_PERIOD_ERR_MSG"))
            except PeriodicMsgJobInvalidStartError:
                await self._SendMessage(self.translator.GetSentence("TASK_START_ERR_MSG"))
            except PeriodicMsgJobMaxNumError:
                await self._SendMessage(self.translator.GetSentence("MAX_TASK_ERR_MSG"))
            except PeriodicMsgJobAlreadyExistentError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "TASK_EXISTENT_ERR_MSG",
                        msg_id=msg_id,
                    ),
                )
            except PeriodicMsgParserInvalidError:
                await self._SendMessage(self.translator.GetSentence("MESSAGE_INVALID_ERR_MSG"))
            except PeriodicMsgParserTooLongError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "MESSAGE_TOO_LONG_ERR_MSG",
                        msg_max_len=self.config.GetValue(BotConfigTypes.MESSAGE_MAX_LEN),
                    ),
                )


class MessageTaskStopCmd(CommandBase):
    """Command for stopping a periodic message task."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task stop command."""
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].Stop(self.cmd_data.Chat(), self.message.message_thread_id, msg_id)
                await self._SendMessage(
                    self.translator.GetSentence(
                        "MESSAGE_TASK_STOP_OK_CMD",
                        msg_id=msg_id,
                    ),
                )
            except PeriodicMsgJobNotExistentError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "TASK_NOT_EXISTENT_ERR_MSG",
                        msg_id=msg_id,
                    ),
                )


class MessageTaskStopAllCmd(CommandBase):
    """Command for stopping all periodic message tasks in a chat."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task stop all command."""
        kwargs["periodic_msg_scheduler"].StopAll(self.cmd_data.Chat())
        await self._SendMessage(
            self.translator.GetSentence("MESSAGE_TASK_STOP_ALL_CMD"),
        )


class MessageTaskPauseCmd(CommandBase):
    """Command for pausing a periodic message task."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task pause command."""
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].Pause(self.cmd_data.Chat(), self.message.message_thread_id, msg_id)
                await self._SendMessage(
                    self.translator.GetSentence(
                        "MESSAGE_TASK_PAUSE_OK_CMD",
                        msg_id=msg_id,
                    ),
                )
            except PeriodicMsgJobNotExistentError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "TASK_NOT_EXISTENT_ERR_MSG",
                        msg_id=msg_id,
                    ),
                )


class MessageTaskResumeCmd(CommandBase):
    """Command for resuming a paused periodic message task."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task resume command."""
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].Resume(self.cmd_data.Chat(), self.message.message_thread_id, msg_id)
                await self._SendMessage(
                    self.translator.GetSentence(
                        "MESSAGE_TASK_RESUME_OK_CMD",
                        msg_id=msg_id,
                    ),
                )
            except PeriodicMsgJobNotExistentError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "TASK_NOT_EXISTENT_ERR_MSG",
                        msg_id=msg_id,
                    ),
                )


class MessageTaskGetCmd(CommandBase):
    """Command for getting the message of a periodic task."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task get command."""
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                msg = kwargs["periodic_msg_scheduler"].GetMessage(self.cmd_data.Chat(),
                                                                  self.message.message_thread_id,
                                                                  msg_id)

                if msg != "":
                    await self._SendMessage(
                        self.translator.GetSentence(
                            "MESSAGE_TASK_GET_OK_CMD",
                            msg_id=msg_id,
                            msg=msg,
                        ),
                    )
                else:
                    await self._SendMessage(
                        self.translator.GetSentence(
                            "MESSAGE_TASK_GET_NO_CMD",
                            msg_id=msg_id,
                        ),
                    )
            except PeriodicMsgJobNotExistentError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "TASK_NOT_EXISTENT_ERR_MSG",
                        msg_id=msg_id,
                    ),
                )


class MessageTaskSetCmd(CommandBase):
    """Command for setting the message of a periodic task."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task set command."""
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].SetMessage(
                    self.cmd_data.Chat(),
                    self.message.message_thread_id,
                    msg_id,
                    self.message,
                )
                await self._SendMessage(
                    self.translator.GetSentence(
                        "MESSAGE_TASK_SET_OK_CMD",
                        msg_id=msg_id,
                    ),
                )
            except PeriodicMsgJobNotExistentError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "TASK_NOT_EXISTENT_ERR_MSG",
                        msg_id=msg_id,
                    ),
                )
            except PeriodicMsgParserInvalidError:
                await self._SendMessage(self.translator.GetSentence("MESSAGE_INVALID_ERR_MSG"))
            except PeriodicMsgParserTooLongError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "MESSAGE_TOO_LONG_ERR_MSG",
                        msg_max_len=self.config.GetValue(BotConfigTypes.MESSAGE_MAX_LEN),
                    ),
                )


class MessageTaskDeleteLastMsgCmd(CommandBase):
    """Command for setting whether to delete the last sent message."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task delete last message command."""
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
            flag = self.cmd_data.Params().GetAsBool(1)
        except CommandParameterError:
            await self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].DeleteLastSentMessage(
                    self.cmd_data.Chat(),
                    self.message.message_thread_id,
                    msg_id,
                    flag,
                )
                await self._SendMessage(
                    self.translator.GetSentence(
                        "MESSAGE_TASK_DELETE_LAST_MSG_OK_CMD",
                        msg_id=msg_id,
                        flag=flag,
                    ),
                )
            except PeriodicMsgJobNotExistentError:
                await self._SendMessage(
                    self.translator.GetSentence(
                        "TASK_NOT_EXISTENT_ERR_MSG",
                        msg_id=msg_id,
                    ),
                )


class MessageTaskInfoCmd(CommandBase):
    """Command for displaying information about periodic message tasks."""

    @override
    @GroupChatOnly
    async def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        """Execute the message task info command."""
        jobs_list = kwargs["periodic_msg_scheduler"].GetJobsInChat(self.cmd_data.Chat())

        if jobs_list.Any():
            await self._SendMessage(
                self.translator.GetSentence(
                    "MESSAGE_TASK_INFO_CMD",
                    tasks_num=jobs_list.Count(),
                    tasks_list=str(jobs_list),
                ),
            )
        else:
            await self._SendMessage(self.translator.GetSentence("MESSAGE_TASK_INFO_NO_TASK_CMD"))
