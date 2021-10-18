# Telegram Periodic Message Bot

[![PyPI version](https://badge.fury.io/py/telegram-periodic-msg-bot.svg)](https://badge.fury.io/py/telegram-periodic-msg-bot)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/d1cc7c1692de4939a23e626981923e83)](https://www.codacy.com/gh/ebellocchia/telegram_periodic_msg_bot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ebellocchia/telegram_periodic_msg_bot&amp;utm_campaign=Badge_Grade)
[![CodeFactor](https://www.codefactor.io/repository/github/ebellocchia/telegram_periodic_msg_bot/badge)](https://www.codefactor.io/repository/github/ebellocchia/telegram_periodic_msg_bot)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://raw.githubusercontent.com/ebellocchia/bip_utils/master/LICENSE)

Telegram bot for sending periodic messages in groups based on *pyrogram*.\
A single bot instance can be used with multiple periodic messages (with different periods) and in multiple groups.

## Setup

### Create Telegram app

In order to use the bot, in addition to the bot token you also need an APP ID and hash.\
To get them, create an app using the following website: [https://my.telegram.org/apps](https://my.telegram.org/apps).

### Installation

The package requires Python 3, it is not compatible with Python 2.\
To install it:
- Using *setuptools*:

        python setup.py install

- Using *pip*:

        pip install telegram_periodic_msg_bot

To run the bot, edit the configuration file by specifying the API ID/hash and bot token. Then, move to the *app* folder and run the *bot.py* script:

    cd app
    python bot.py

When run with no parameter, *conf/config.ini* will be the default configuration file (in this way it can be used for different groups).\
To specify a different configuration file:

    python bot.py -c another_conf.ini
    python bot.py --config another_conf.ini

Of course, the *app* folder can be moved elsewhere if needed.

## Configuration

An example of configuration file is provided in the *app/conf* folder.\
The list of all possible fields that can be set is shown below.

|Name|Description|
|---|---|
|**[pyrogram]**|Configuration for pyrogram|
|session_name|Session name of your choice|
|api_id|API ID from [https://my.telegram.org/apps](https://my.telegram.org/apps)|
|api_hash|API hash from [https://my.telegram.org/apps](https://my.telegram.org/apps)|
|bot_token|Bot token from BotFather|
|**[app]**|Configuration for app|
|app_is_test_mode|True to activate test mode false otherwise|
|app_lang_file|Language file in XML format (default: English)|
|**[task]**|Configuration for tasks|
|tasks_max_num|Maximum number of running tasks (totally, in all groups). Default: 20.|
|**[message]**|Configuration for message|
|message_max_len|Maximum message length in characters. Default: 4000.|
|**[logging]**|Configuration for logging|
|log_level|Log level, same of python logging (*DEBUG*, *INFO*, *WARNING*, *ERROR*, *CRITICAL*). Default: *INFO*.|
|log_console_enabled|True to enable logging to console, false otherwise (default: true)|
|log_file_enabled|True to enable logging to file, false otherwise (default: false). If false, all the next fields will be skipped.|
|log_file_name|Log file name|
|log_file_use_rotating|True for using a rotating log file, false otherwise|
|log_file_max_bytes|Maximum size in bytes for a log file. When reached, a new log file is created up to *log_file_backup_cnt*.. Valid only if log_file_use_rotating is true.|
|log_file_backup_cnt|Maximum number of log files. Valid only if log_file_use_rotating is true.|
|log_file_append|True to append to log file, false to start from a new file each time. Valid only if log_file_use_rotating is false.|

## Supported Commands

List of supported commands:
- **/help**: show this message
- **/alive**: show if bot is active
- **/set_test_mode true/false**: enable/disable test mode
- **/is_test_mode**: show if test mode is enabled
- **/message_task_start *PERIOD_HOURS MSG_ID MSG***: start a message task in the current chat. If the task *MSG_ID* already exists in the current chat, an error message will be shown. To start it again, it shall be stopped with the *message_task_stop* command.
    - *PERIOD_HOURS*: Task period in hours, it shall be between 1 and 24
    - *MSG_ID*: Message ID
    - *MSG*: Message to be sent periodically, it shall be on a new line
- **/message_task_stop *MSG_ID***: stop the specified message task in the current chat. If the task *MSG_ID* does not exist in the current chat, an error message will be shown.
    - *MSG_ID*: CoinGecko *ID*
- **/message_task_stop_all**: stop all message tasks in the current chat
- **/message_task_pause *MSG_ID***: pause the specified message task in the current chat. If the task *MSG_ID* does not exist in the current chat, an error message will be shown.
    - *MSG_ID*: Message ID
- **/message_task_resume *MSG_ID***: resume the specified message task in the current chat. If the task *MSG_ID* does not exist in the current chat, an error message will be shown.
    - *MSG_ID*: Message ID
- **/message_task_get *MSG_ID***: show the message set for the specified message task in the current chat.
    - *MSG_ID*: Message ID
- **/message_task_set *MSG_ID MSG***: set the message of the specified message task in the current chat
    - *MSG_ID*: Message ID
    - *MSG*: Message to be sent periodically, it shall be on a new line
- **/message_task_delete_last_msg *MSG_ID true/false***: enable/disable the deletion of last messages for the specified message task in the current chat. If the task *MSG_ID* does not exist in the current chat, an error message will be shown.
    - *MSG_ID*: Message ID
    - *flag*: true or false
- **/message_task_info**: show the list of active message tasks in the current chat

Messages can contain HTML tags if needed (e.g. for bold/italic text), while Markdown tags are not supported.\
By default, a message task will delete the last sent message when sending a new one. This can be enabled/disabled with the *message_task_delete_last_msg* command.

The task period always starts from midnight (be sure to set the correct time on the VPS), for example:
- A task period of 8 hours will send the message at 00:00, 08:00 and 16:00
- A task period of 6 hours will send the message at 00:00, 06:00, 12:00 and 18:00

**Examples**

Send a periodical message every 8 hours in the current chat:

    /message_task_start 1 test_msg
    Hi,
    This is a <i>periodic message</i>.
    <b>Bye!</b>

Pause/Resume/Stop the previous task:

    /message_task_pause test_msg
    /message_task_resume test_msg
    /message_task_stop test_msg

Show the message set for the previous task:

    /message_task_get test_msg

Set a new message set for the previous task:

    /message_task_set test_msg
    Hello,
    This is a <i>different periodic message</i>.
    <b>Bye bye!</b>

Set task so that it doesn't delete the last sent message:

    /message_task_delete_last_msg test_msg false

## Run the Bot

It'd be better if the bot is an administrator of the group. This is mandatory if it needs to delete the last sent messages.\
In order to send messages periodically, the bot shall run 24h/24h so it's suggested to run it on a VPS (there is no performance requirements, so a cheap VPS will suffice).

## Test Mode

During test mode, the bot will work as usual but the task period will be applied in minutes instead of hours. This allows to quickly check if it is working.

## Translation

The messages sent by the bot on Telegram can be translated into different languages (the default language is English) by providing a custom XML file.\
The XML file path is specified in the configuration file (*app_lang_file* field).\
An example XML file in italian is provided in the folder *app/lang*.

# License

This software is available under the MIT license.
