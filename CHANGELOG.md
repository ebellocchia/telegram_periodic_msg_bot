# 0.4.0

- Migrate to full async/await client
- Topics support: if bot is started in a topic, it'll send messages in that specific topic (not in General like before).\
  All task commands operates in the topic where they are executed.

# 0.3.5

- Use `pyrotgfork`, since `pyrogram` was archived

# 0.3.4

- Update Python versions

# 0.3.3

- Fix replying to commands in topics

# 0.3.2

- Fix usage in channels

# 0.3.1

- Fix some _mypy_ and _prospector_ warnings
- Add configuration for _isort_ and run it on project

# 0.3.0

- Add support for _pyrogram_ version 2 (version 1 still supported)

# 0.2.4

- Bot can now work in channels

# 0.2.3

- Handle anonymous user case when executing a command

# 0.2.2

- Add command for showing bot version

# 0.2.1

- Project re-organized into folders

# 0.2.0

- Add possibility to specify a starting hour for message tasks

# 0.1.5

- Add single handlers for message updates, to avoid being notified of each single message sent in groups

# 0.1.4

- Rename commands by adding the `msgbot_` prefix, to avoid conflicts with other bots

# 0.1.3

- Add configuration files for _flake8_ and prospector
- Fix all _flake8_ warnings
- Fix the vast majority of _prospector_ warnings
- Remove all star imports (`import *`)

# 0.1.2

- Fix wrong imports
- Add typing to class members
- Fix _mypy_ errors

# 0.1.1

- Minor bug fixes

# 0.1.0

First release
