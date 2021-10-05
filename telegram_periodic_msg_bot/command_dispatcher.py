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
from enum import Enum, auto, unique
from typing import Any, Dict, Type
from telegram_periodic_msg_bot.command_base import CommandBase
from telegram_periodic_msg_bot.commands import *
from telegram_periodic_msg_bot.config import Config
from telegram_periodic_msg_bot.logger import Logger
from telegram_periodic_msg_bot.translation_loader import TranslationLoader


#
# Enumerations
#

# Command types
@unique
class CommandTypes(Enum):
    START_CMD = auto()
    HELP_CMD = auto()
    ALIVE_CMD = auto()
    SET_TEST_MODE_CMD = auto()
    IS_TEST_MODE_CMD = auto()
    MESSAGE_TASK_START_CMD = auto()
    MESSAGE_TASK_STOP_CMD = auto()
    MESSAGE_TASK_STOP_ALL_CMD = auto()
    MESSAGE_TASK_PAUSE_CMD = auto()
    MESSAGE_TASK_RESUME_CMD = auto()
    MESSAGE_TASK_GET_CMD = auto()
    MESSAGE_TASK_SET_CMD = auto()
    MESSAGE_TASK_DELETE_LAST_MSG_CMD = auto()
    MESSAGE_TASK_INFO_CMD = auto()


#
# Classes
#

# Comstant for command dispatcher class
class CommandDispatcherConst:
    # Command to class map
    CMD_TYPE_TO_CLASS: Dict[CommandTypes, Type[CommandBase]] = {
        CommandTypes.START_CMD: HelpCmd,
        CommandTypes.HELP_CMD: HelpCmd,
        CommandTypes.ALIVE_CMD: AliveCmd,
        CommandTypes.SET_TEST_MODE_CMD: SetTestModeCmd,
        CommandTypes.IS_TEST_MODE_CMD: IsTestModeCmd,
        CommandTypes.MESSAGE_TASK_START_CMD: MessageTaskStartCmd,
        CommandTypes.MESSAGE_TASK_STOP_CMD: MessageTaskStopCmd,
        CommandTypes.MESSAGE_TASK_STOP_ALL_CMD: MessageTaskStopAllCmd,
        CommandTypes.MESSAGE_TASK_PAUSE_CMD: MessageTaskPauseCmd,
        CommandTypes.MESSAGE_TASK_RESUME_CMD: MessageTaskResumeCmd,
        CommandTypes.MESSAGE_TASK_GET_CMD: MessageTaskGetCmd,
        CommandTypes.MESSAGE_TASK_SET_CMD: MessageTaskSetCmd,
        CommandTypes.MESSAGE_TASK_DELETE_LAST_MSG_CMD: MessageTaskDeleteLastMsgCmd,
        CommandTypes.MESSAGE_TASK_INFO_CMD: MessageTaskInfoCmd,
    }


# Command dispatcher class
class CommandDispatcher:
    # Constructor
    def __init__(self,
                 config: Config,
                 logger: Logger,
                 translator: TranslationLoader) -> None:
        self.config = config
        self.logger = logger
        self.translator = translator

    # Dispatch command
    def Dispatch(self,
                 client: pyrogram.Client,
                 message: pyrogram.types.Message,
                 cmd_type: CommandTypes,
                 **kwargs: Any) -> None:
        if not isinstance(cmd_type, CommandTypes):
            raise TypeError("Command type is not an enumerative of CommandTypes")

        # Create and execute command if existent
        if cmd_type in CommandDispatcherConst.CMD_TYPE_TO_CLASS:
            cmd_class = CommandDispatcherConst.CMD_TYPE_TO_CLASS[cmd_type](client,
                                                                           self.config,
                                                                           self.logger,
                                                                           self.translator)
            cmd_class.Execute(message, **kwargs)
