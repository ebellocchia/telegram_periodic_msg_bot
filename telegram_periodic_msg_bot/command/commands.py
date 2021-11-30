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
from typing import Any, Callable

from telegram_periodic_msg_bot.command.command_base import CommandBase
from telegram_periodic_msg_bot.command.command_data import CommandParameterError
from telegram_periodic_msg_bot.bot.bot_config import BotConfigTypes
from telegram_periodic_msg_bot.misc.helpers import UserHelper
from telegram_periodic_msg_bot.periodic_msg.periodic_msg_scheduler import (
    PeriodicMsgJobAlreadyExistentError, PeriodicMsgJobNotExistentError,
    PeriodicMsgJobInvalidPeriodError, PeriodicMsgJobInvalidStartError,
    PeriodicMsgJobMaxNumError
)
from telegram_periodic_msg_bot.periodic_msg.periodic_msg_parser import (
    PeriodicMsgParserInvalidError, PeriodicMsgParserTooLongError
)


#
# Decorators
#

# Decorator for group-only commands
def GroupChatOnly(exec_cmd_fct: Callable[..., None]) -> Callable[..., None]:
    def decorated(self,
                  **kwargs: Any):
        # Check if private chat
        if self._IsPrivateChat():
            self._SendMessage(self.translator.GetSentence("GROUP_ONLY_ERR_MSG"))
        else:
            exec_cmd_fct(self, **kwargs)

    return decorated


#
# Classes
#

#
# Command for getting help
#
class HelpCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(
            self.translator.GetSentence("HELP_CMD",
                                        name=UserHelper.GetName(self.cmd_data.User()))
        )


#
# Command for checking if bot is alive
#
class AliveCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        self._SendMessage(self.translator.GetSentence("ALIVE_CMD"))


#
# Command for setting test mode
#
class SetTestModeCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        try:
            # Get parameters
            flag = self.cmd_data.Params().GetAsBool(0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            # Set test mode
            self.config.SetValue(BotConfigTypes.APP_TEST_MODE, flag)

            # Send message
            if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
                self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_EN_CMD"))
            else:
                self._SendMessage(self.translator.GetSentence("SET_TEST_MODE_DIS_CMD"))


#
# Command for checking if test mode
#
class IsTestModeCmd(CommandBase):
    # Execute command
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        if self.config.GetValue(BotConfigTypes.APP_TEST_MODE):
            self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_EN_CMD"))
        else:
            self._SendMessage(self.translator.GetSentence("IS_TEST_MODE_DIS_CMD"))


#
# Message task start command
#
class MessageTaskStartCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
            period_hours = self.cmd_data.Params().GetAsInt(1)
            start_hour = self.cmd_data.Params().GetAsInt(2, 0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].Start(self.cmd_data.Chat(),
                                                       period_hours,
                                                       start_hour,
                                                       msg_id,
                                                       self.message)
                self._SendMessage(
                    self.translator.GetSentence("MESSAGE_TASK_START_OK_CMD",
                                                period=period_hours,
                                                start=start_hour,
                                                msg_id=msg_id)
                )
            except PeriodicMsgJobInvalidPeriodError:
                self._SendMessage(self.translator.GetSentence("TASK_PERIOD_ERR_MSG"))
            except PeriodicMsgJobInvalidStartError:
                self._SendMessage(self.translator.GetSentence("TASK_START_ERR_MSG"))
            except PeriodicMsgJobMaxNumError:
                self._SendMessage(self.translator.GetSentence("MAX_TASK_ERR_MSG"))
            except PeriodicMsgJobAlreadyExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_EXISTENT_ERR_MSG",
                                                msg_id=msg_id)
                )
            except PeriodicMsgParserInvalidError:
                self._SendMessage(self.translator.GetSentence("MESSAGE_INVALID_ERR_MSG"))
            except PeriodicMsgParserTooLongError:
                self._SendMessage(
                    self.translator.GetSentence("MESSAGE_TOO_LONG_ERR_MSG",
                                                msg_max_len=self.config.GetValue(BotConfigTypes.MESSAGE_MAX_LEN))
                )


#
# Message task stop command
#
class MessageTaskStopCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].Stop(self.cmd_data.Chat(), msg_id)
                self._SendMessage(
                    self.translator.GetSentence("MESSAGE_TASK_STOP_OK_CMD",
                                                msg_id=msg_id)
                )
            except PeriodicMsgJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                msg_id=msg_id)
                )


#
# Message task stop all command
#
class MessageTaskStopAllCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        kwargs["periodic_msg_scheduler"].StopAll(self.cmd_data.Chat())
        self._SendMessage(
            self.translator.GetSentence("MESSAGE_TASK_STOP_ALL_CMD")
        )


#
# Message task pause command
#
class MessageTaskPauseCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].Pause(self.cmd_data.Chat(), msg_id)
                self._SendMessage(
                    self.translator.GetSentence("MESSAGE_TASK_PAUSE_OK_CMD",
                                                msg_id=msg_id)
                )
            except PeriodicMsgJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                msg_id=msg_id)
                )


#
# Message task resume command
#
class MessageTaskResumeCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].Resume(self.cmd_data.Chat(), msg_id)
                self._SendMessage(
                    self.translator.GetSentence("MESSAGE_TASK_RESUME_OK_CMD",
                                                msg_id=msg_id)
                )
            except PeriodicMsgJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                msg_id=msg_id)
                )


#
# Message task get command
#
class MessageTaskGetCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                msg = kwargs["periodic_msg_scheduler"].GetMessage(self.cmd_data.Chat(), msg_id)

                if msg != "":
                    self._SendMessage(
                        self.translator.GetSentence("MESSAGE_TASK_GET_OK_CMD",
                                                    msg_id=msg_id,
                                                    msg=msg)
                    )
                else:
                    self._SendMessage(
                        self.translator.GetSentence("MESSAGE_TASK_GET_NO_CMD",
                                                    msg_id=msg_id)
                    )
            except PeriodicMsgJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                msg_id=msg_id)
                )


#
# Message task set command
#
class MessageTaskSetCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].SetMessage(self.cmd_data.Chat(),
                                                            msg_id,
                                                            self.message)
                self._SendMessage(
                    self.translator.GetSentence("MESSAGE_TASK_SET_OK_CMD",
                                                msg_id=msg_id)
                )
            except PeriodicMsgJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                msg_id=msg_id)
                )
            except PeriodicMsgParserInvalidError:
                self._SendMessage(self.translator.GetSentence("MESSAGE_INVALID_ERR_MSG"))
            except PeriodicMsgParserTooLongError:
                self._SendMessage(
                    self.translator.GetSentence("MESSAGE_TOO_LONG_ERR_MSG",
                                                msg_max_len=self.config.GetValue(BotConfigTypes.MESSAGE_MAX_LEN))
                )


#
# Message task delete last message command
#
class MessageTaskDeleteLastMsgCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        # Get parameters
        try:
            msg_id = self.cmd_data.Params().GetAsString(0)
            flag = self.cmd_data.Params().GetAsBool(1)
        except CommandParameterError:
            self._SendMessage(self.translator.GetSentence("PARAM_ERR_MSG"))
        else:
            try:
                kwargs["periodic_msg_scheduler"].DeleteLastSentMessage(self.cmd_data.Chat(), msg_id, flag)
                self._SendMessage(
                    self.translator.GetSentence("MESSAGE_TASK_DELETE_LAST_MSG_OK_CMD",
                                                msg_id=msg_id,
                                                flag=flag)
                )
            except PeriodicMsgJobNotExistentError:
                self._SendMessage(
                    self.translator.GetSentence("TASK_NOT_EXISTENT_ERR_MSG",
                                                msg_id=msg_id)
                )


#
# Message task info command
#
class MessageTaskInfoCmd(CommandBase):
    # Execute command
    @GroupChatOnly
    def _ExecuteCommand(self,
                        **kwargs: Any) -> None:
        jobs_list = kwargs["periodic_msg_scheduler"].GetJobsInChat(self.cmd_data.Chat())

        if jobs_list.Any():
            self._SendMessage(
                self.translator.GetSentence("MESSAGE_TASK_INFO_CMD",
                                            tasks_num=jobs_list.Count(),
                                            tasks_list=str(jobs_list))
            )
        else:
            self._SendMessage(self.translator.GetSentence("MESSAGE_TASK_INFO_NO_TASK_CMD"))
