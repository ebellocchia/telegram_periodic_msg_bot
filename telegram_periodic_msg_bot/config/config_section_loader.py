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

import configparser

from telegram_periodic_msg_bot.config.config_loader_ex import ConfigFieldNotExistentError, ConfigFieldValueError
from telegram_periodic_msg_bot.config.config_object import ConfigObject
from telegram_periodic_msg_bot.config.config_typing import ConfigFieldType, ConfigSectionType


class ConfigSectionLoader:
    """Loader class for processing individual configuration sections."""

    config_parser: configparser.ConfigParser

    def __init__(self,
                 config_parser: configparser.ConfigParser) -> None:
        """
        Initialize the section loader with a configuration parser.

        Args:
            config_parser: ConfigParser instance containing the parsed configuration
        """
        self.config_parser = config_parser

    def LoadSection(self,
                    config_obj: ConfigObject,
                    section_name: str,
                    section: ConfigSectionType) -> None:
        """
        Load all fields from a configuration section into the config object.

        Args:
            config_obj: Configuration object to populate
            section_name: Name of the section in the configuration file
            section: Section specification containing field definitions
        """
        for field in section:
            if self.__FieldShallBeLoaded(config_obj, field):
                self.__SetFieldValue(config_obj, section_name, field)
                self.__PrintFieldValue(config_obj, field)
            elif "def_val" in field:
                config_obj.SetValue(field["type"], field["def_val"])

    @staticmethod
    def __FieldShallBeLoaded(config_obj: ConfigObject,
                             field: ConfigFieldType) -> bool:
        """
        Determine if a field should be loaded based on its conditional logic.

        Args:
            config_obj: Current configuration object
            field: Field specification

        Returns:
            True if the field should be loaded, False otherwise
        """
        return field["load_if"](config_obj) if "load_if" in field else True

    def __SetFieldValue(self,
                        config_obj: ConfigObject,
                        section: str,
                        field: ConfigFieldType) -> None:
        """
        Read, convert, validate and set a field value in the configuration object.

        Args:
            config_obj: Configuration object to update
            section: Section name in the configuration file
            field: Field specification

        Raises:
            ConfigFieldNotExistentError: If a required field is not found
            ConfigFieldValueError: If the field value fails validation
        """
        try:
            field_val = self.config_parser[section][field["name"]]
        except KeyError as ex:
            if "def_val" not in field:
                raise ConfigFieldNotExistentError(f"Configuration field \"{field['name']}\" not found") from ex
            field_val = field["def_val"]
        else:
            if "conv_fct" in field:
                field_val = field["conv_fct"](field_val)

        if "valid_if" in field and not field["valid_if"](config_obj, field_val):
            raise ConfigFieldValueError(f"Value '{field_val}' is not valid for field \"{field['name']}\"")

        config_obj.SetValue(field["type"], field_val)

    @staticmethod
    def __PrintFieldValue(config_obj: ConfigObject,
                          field: ConfigFieldType) -> None:
        """
        Print the loaded field value to the console.

        Args:
            config_obj: Configuration object containing the value
            field: Field specification with optional print function
        """
        if "print_fct" in field:
            print(f"- {field['name']}: {field['print_fct'](config_obj.GetValue(field['type']))}")
        else:
            print(f"- {field['name']}: {config_obj.GetValue(field['type'])}")
