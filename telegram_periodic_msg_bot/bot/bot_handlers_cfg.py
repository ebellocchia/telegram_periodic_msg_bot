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
from pyrogram import filters
from pyrogram.handlers import MessageHandler
from telegram_periodic_msg_bot.bot.bot_base import HandlersCfgType
from telegram_periodic_msg_bot.command.command_dispatcher import CommandTypes
from telegram_periodic_msg_bot.message.message_dispatcher import MessageTypes


#
# Classes
#

# Bot handlers configuration
BotHandlersCfg: HandlersCfgType = {
    # Handlers for MessageHandler
    MessageHandler: [

        #
        # Generic commands
        #

        {
            "callback": lambda self, client, message: self.DispatchCommand(client,
                                                                           message,
                                                                           CommandTypes.START_CMD),
            "filters": filters.private & filters.command(["start"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client,
                                                                           message,
                                                                           CommandTypes.HELP_CMD),
            "filters": filters.command(["help"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client,
                                                                           message,
                                                                           CommandTypes.ALIVE_CMD),
            "filters": filters.command(["alive"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client,
                                                                           message,
                                                                           CommandTypes.SET_TEST_MODE_CMD),
            "filters": filters.command(["msgbot_set_test_mode"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client,
                                                                           message,
                                                                           CommandTypes.IS_TEST_MODE_CMD),
            "filters": filters.command(["msgbot_is_test_mode"]),
        },
        {
            "callback": lambda self, client, message: self.DispatchCommand(client,
                                                                           message,
                                                                           CommandTypes.VERSION_CMD),
            "filters": filters.command(["msgbot_version"]),
        },

        #
        # Message commands (task)
        #

        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_START_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_start"]),
        },
        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_STOP_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_stop"]),
        },
        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_STOP_ALL_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_stop_all"]),
        },
        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_PAUSE_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_pause"]),
        },
        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_RESUME_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_resume"]),
        },
        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_GET_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_get"]),
        },
        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_SET_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_set"]),
        },
        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_DELETE_LAST_MSG_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_delete_last_msg"]),
        },
        {
            "callback": (lambda self, client, message: self.DispatchCommand(client,
                                                                            message,
                                                                            CommandTypes.MESSAGE_TASK_INFO_CMD,
                                                                            periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.command(["msgbot_task_info"]),
        },

        #
        # Update status messages
        #

        {
            "callback": (lambda self, client, message: self.HandleMessage(client,
                                                                          message,
                                                                          MessageTypes.GROUP_CHAT_CREATED)),
            "filters": filters.group_chat_created,
        },
        {
            "callback": (lambda self, client, message: self.HandleMessage(client,
                                                                          message,
                                                                          MessageTypes.NEW_CHAT_MEMBERS)),
            "filters": filters.new_chat_members,
        },
        {
            "callback": (lambda self, client, message: self.HandleMessage(client,
                                                                          message,
                                                                          MessageTypes.LEFT_CHAT_MEMBER,
                                                                          periodic_msg_scheduler=self.periodic_msg_scheduler)),
            "filters": filters.left_chat_member,
        },
    ],
}
