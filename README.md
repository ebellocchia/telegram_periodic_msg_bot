# Telegram Periodic Message Bot

| |
|---|
| [![PyPI - Version](https://img.shields.io/pypi/v/telegram_periodic_msg_bot.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/telegram_periodic_msg_bot/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/telegram_periodic_msg_bot.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/telegram_periodic_msg_bot/) [![GitHub License](https://img.shields.io/github/license/ebellocchia/telegram_periodic_msg_bot?label=License)](https://github.com/ebellocchia/telegram_periodic_msg_bot?tab=MIT-1-ov-file) |
| [![Build](https://github.com/ebellocchia/telegram_periodic_msg_bot/actions/workflows/build.yml/badge.svg)](https://github.com/ebellocchia/telegram_periodic_msg_bot/actions/workflows/build.yml) [![Code Analysis](https://github.com/ebellocchia/telegram_periodic_msg_bot/actions/workflows/code-analysis.yml/badge.svg)](https://github.com/ebellocchia/telegram_periodic_msg_bot/actions/workflows/code-analysis.yml) |
| [![Codacy grade](https://img.shields.io/codacy/grade/d1cc7c1692de4939a23e626981923e83?label=Codacy%20Grade)](https://app.codacy.com/gh/ebellocchia/telegram_periodic_msg_bot/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade) [![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/ebellocchia/telegram_periodic_msg_bot?label=CodeFactor%20Grade)](https://www.codefactor.io/repository/github/ebellocchia/telegram_periodic_msg_bot) |
| |

## Introduction

Telegram bot for sending periodic text messages in groups based on *pyrotgfork* (a maintained fork of the *pyrogram* library).

A single bot instance can handle multiple periodic messages (with different periods) across multiple groups.

## Setup

### Create Telegram app

In order to use the bot, you need a Telegram bot token, an API ID, and an API hash.

To obtain them, create an app on the following website: [https://my.telegram.org/apps](https://my.telegram.org/apps).

### Installation

This package requires **Python >= 3.7**.


1. **Set up a virtual environment (optional but recommended)**:

```
python -m venv venv
source venv/bin/activate    # On Windows use: venv\Scripts\activate
```

2. **Install the bot:**

```
pip install telegram_periodic_msg_bot
```

**IMPORTANT NOTE:** This bot uses *pyrotgfork*. If you are not using a virtual environment, ensure that the standard *pyrogram* library (or forks) is not installed in your Python environment.
Since both libraries use the same package name, having both installed will cause conflicts and the bot will not function correctly.

3. **Set up the bot:**
Copy the **app** folder from the repository to your device. Edit the configuration file by specifying your API ID, API hash, bot token, and other parameters according to your needs (see the "Configuration" chapter).
4. **Run the bot:**
Inside the **app** folder, launch the **bot_start.py** script to start the bot:

```
python bot_start.py
```

---

#### Custom Configuration

When run without parameters, the bot uses **conf/config.ini** as the default configuration file. To specify a different configuration file, use:

```
python bot_start.py -c another_conf.ini
```

or:

```
python bot_start.py --config another_conf.ini
```

This allows you to manage different bots easily, each one with its own configuration file.

### Code analysis

To run code analysis:

```
mypy .
ruff check .
```

## Configuration

An example configuration file is provided in the **app/conf** folder.

The list of all configurable fields is shown below.

| Name | Description |
| --- | --- |
| **[pyrogram]** | Configuration for pyrogram |
| `session_name` | Name of the file used to store the session |
| `api_id` | API ID from [https://my.telegram.org/apps](https://my.telegram.org/apps) |
| `api_hash` | API hash from [https://my.telegram.org/apps](https://my.telegram.org/apps) |
| `bot_token` | Bot token from BotFather |
| **[app]** | Configuration for app |
| `app_is_test_mode` | True to activate test mode, false otherwise |
| `app_lang_file` | Language file in XML format. Default: English. |
| **[task]** | Configuration for tasks |
| `tasks_max_num` | Maximum number of running tasks (total, in all groups). Default: `20`. |
| **[message]** | Configuration for message |
| `message_max_len` | Maximum message length in characters. Default: `4000`. |
| **[logging]** | Configuration for logging |
| `log_level` | Log level, same as python logging (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`). Default: `INFO`. |
| `log_console_enabled` | True to enable logging to console, false otherwise (default: `true`) |
| `log_file_enabled` | True to enable logging to file, false otherwise (default: `false`). If false, the following fields will be ignored. |
| `log_file_name` | Log file name |
| `log_file_use_rotating` | True to use a rotating log file, false otherwise |
| `log_file_max_bytes` | Maximum size in bytes for a log file. When reached, a new log file is created up to `log_file_backup_cnt`. Only valid if `log_file_use_rotating` is true. |
| `log_file_backup_cnt` | Maximum number of log files. Only valid if `log_file_use_rotating` is true. |
| `log_file_append` | True to append to the log file, false to start fresh each time. Only valid if `log_file_use_rotating` is false. |

## Supported Commands

List of supported commands:
- `help`: show this message
- `alive`: show if the bot is active
- `msgbot_set_test_mode true/false`: enable/disable test mode
- `msgbot_is_test_mode`: show if test mode is enabled
- `msgbot_version`: show the bot version
- `msgbot_task_start MSG_ID PERIOD_HOURS [START_HOUR] MSG`: start a message task (in the current chat/topic). If the `MSG_ID` already exists, an error message will be shown. To restart it, you must first stop it with the `msgbot_task_stop` command.
    - `MSG_ID`: Message ID
    - `PERIOD_HOURS`: Task period in hours (must be between 1 and 24)
    - `START_HOUR` (optional): Task start hour (must be between 0 and 23). Default value: 0.
    - `MSG`: Message to be sent periodically (must be on a new line)
- `msgbot_task_stop MSG_ID`: stop the specified message task (in the current chat/topic).
    - `MSG_ID`: Message ID
- `msgbot_task_stop_all`: stop all message tasks in the current chat (all topics included).
- `msgbot_task_pause MSG_ID`: pause the specified message task.
    - `MSG_ID`: Message ID
- `msgbot_task_resume MSG_ID`: resume the specified message task (in the current chat/topic).
    - `MSG_ID`: Message ID
- `msgbot_task_get MSG_ID`: show the message content for the specified message task (in the current chat/topic).
    - `MSG_ID`: Message ID
- `msgbot_task_set MSG_ID MSG`: update the message for the specified message task (in the current chat/topic).
    - `MSG_ID`: Message ID
    - `MSG`: New message to be sent (must be on a new line)
- `msgbot_task_delete_last_msg MSG_ID true/false`: enable/disable the deletion of the previous message when a new one is sent for the specified message task (in the current chat/topic).
    - `MSG_ID`: Message ID
    - `flag`: `true` or `false`
- `msgbot_task_info`: show the list of active message tasks in the current chat.

Messages can contain HTML tags (e.g., `<b>`, `<i>`), but Markdown is not supported.
By default, the bot deletes the last sent message when sending a new one. This can be toggled using the `msgbot_task_delete_last_msg` command.

**Scheduling Logic:**
The task period starts from the specified hour (ensure the VPS time is correct):

- Period of 8h starting at 00:00: sends at 00:00, 08:00, 16:00
- Period of 6h starting at 10:00: sends at 10:00, 16:00, 22:00, 04:00

**Examples**

Start a task every 8 hours:

```
/msgbot_task_start test_msg 8
Hi,
This is a <i>periodic message</i>.
<b>Bye!</b>
```

Stop the task:

```
/msgbot_task_stop test_msg
```

## Run the Bot

The bot should be a group administrator to ensure it has the permissions to delete previous messages.

It is recommended to run the bot 24/7 on a VPS.

### Docker

Docker files are provided to run the bot in a container. You can specify the configuration file via the `CONFIG_FILE` variable:

```
CONFIG_FILE=conf/config.ini docker compose up -d --build
```

**NOTE:** Adjust the `TZ=Europe/Rome` variable in `docker-compose.yml` to match your timezone.

## Test Mode

In test mode, the task period is applied in **minutes** instead of hours, allowing for rapid testing.

## Translation

Bot messages can be translated using a custom XML file specified in the `app_lang_file` field. An Italian example is provided in **app/lang**.

# License

This software is available under the MIT license.
