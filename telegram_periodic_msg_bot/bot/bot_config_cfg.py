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
import logging
from telegram_periodic_msg_bot.bot.bot_config import BotConfigTypes
from telegram_periodic_msg_bot.config.config_loader import ConfigCfgType
from telegram_periodic_msg_bot.utils.key_value_converter import KeyValueConverter
from telegram_periodic_msg_bot.utils.utils import Utils


#
# Variables
#

# Logging level converter
LoggingLevelConverter = KeyValueConverter({
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
})


# Bot configuration
BotConfigCfg: ConfigCfgType = {
    # Pyrogram
    "pyrogram": [
        {
            "type": BotConfigTypes.API_ID,
            "name": "api_id",
        },
        {
            "type": BotConfigTypes.API_HASH,
            "name": "api_hash",
        },
        {
            "type": BotConfigTypes.BOT_TOKEN,
            "name": "bot_token",
        },
        {
            "type": BotConfigTypes.SESSION_NAME,
            "name": "session_name",
        },
    ],
    # App
    "app": [
        {
            "type": BotConfigTypes.APP_TEST_MODE,
            "name": "app_test_mode",
            "conv_fct": Utils.StrToBool,
        },
        {
            "type": BotConfigTypes.APP_LANG_FILE,
            "name": "app_lang_file",
            "def_val": None,
        },
    ],
    # Task
    "task": [
        {
            "type": BotConfigTypes.TASKS_MAX_NUM,
            "name": "tasks_max_num",
            "conv_fct": Utils.StrToInt,
            "def_val": 20,
            "valid_if": lambda cfg, val: val > 0,
        },
    ],
    # Message
    "message": [
        {
            "type": BotConfigTypes.MESSAGE_MAX_LEN,
            "name": "message_max_len",
            "conv_fct": Utils.StrToInt,
            "def_val": 4000,
            "valid_if": lambda cfg, val: val > 0,
        },
    ],
    # Logging
    "logging": [
        {
            "type": BotConfigTypes.LOG_LEVEL,
            "name": "log_level",
            "conv_fct": LoggingLevelConverter.KeyToValue,
            "print_fct": LoggingLevelConverter.ValueToKey,
            "def_val": logging.INFO,
        },
        {
            "type": BotConfigTypes.LOG_CONSOLE_ENABLED,
            "name": "log_console_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": True,
        },
        {
            "type": BotConfigTypes.LOG_FILE_ENABLED,
            "name": "log_file_enabled",
            "conv_fct": Utils.StrToBool,
            "def_val": False,
        },
        {
            "type": BotConfigTypes.LOG_FILE_NAME,
            "name": "log_file_name",
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED),
        },
        {
            "type": BotConfigTypes.LOG_FILE_USE_ROTATING,
            "name": "log_file_use_rotating",
            "conv_fct": Utils.StrToBool,
            "load_if": lambda cfg: cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED),
        },
        {
            "type": BotConfigTypes.LOG_FILE_APPEND,
            "name": "log_file_append",
            "conv_fct": Utils.StrToBool,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and
                                    not cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)),
        },
        {
            "type": BotConfigTypes.LOG_FILE_MAX_BYTES,
            "name": "log_file_max_bytes",
            "conv_fct": Utils.StrToInt,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and
                                    cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)),
        },
        {
            "type": BotConfigTypes.LOG_FILE_BACKUP_CNT,
            "name": "log_file_backup_cnt",
            "conv_fct": Utils.StrToInt,
            "load_if": lambda cfg: (cfg.GetValue(BotConfigTypes.LOG_FILE_ENABLED) and
                                    cfg.GetValue(BotConfigTypes.LOG_FILE_USE_ROTATING)),
        },
    ],
}
