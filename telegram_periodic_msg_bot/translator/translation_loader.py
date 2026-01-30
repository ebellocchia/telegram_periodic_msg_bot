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

import os
from typing import Any, Dict, Optional

from defusedxml import ElementTree

from telegram_periodic_msg_bot.logger.logger import Logger


class TranslationLoaderConst:
    """Constants for translation loader configuration."""

    DEF_LANG_FOLDER: str = "../lang"
    DEF_FILE_NAME: str = "lang_en.xml"
    SENTENCE_XML_TAG: str = "sentence"


class TranslationLoader:
    """Loader for localized translation strings from XML files."""

    logger: Logger
    sentences: Dict[str, str]

    def __init__(self,
                 logger: Logger) -> None:
        """
        Initialize the translation loader.

        Args:
            logger: Logger instance for logging operations
        """
        self.logger = logger
        self.sentences = {}

    def Load(self,
             file_name: Optional[str] = None) -> None:
        """
        Load a translation file, falling back to default if file is not found.

        Args:
            file_name: Optional path to the translation file. If None, loads default language file.
        """
        def_file_path = os.path.join(os.path.dirname(__file__),
                                     TranslationLoaderConst.DEF_LANG_FOLDER,
                                     TranslationLoaderConst.DEF_FILE_NAME)

        if file_name is not None:
            try:
                self.logger.GetLogger().info(f"Loading language file '{file_name}'...")
                self.__LoadFile(file_name)
            except FileNotFoundError:
                self.logger.GetLogger().error(
                    f"Language file '{file_name}' not found, loading default language..."
                )
                self.__LoadFile(def_file_path)
        else:
            self.logger.GetLogger().info("Loading default language file...")
            self.__LoadFile(def_file_path)

    def GetSentence(self,
                    sentence_id: str,
                    **kwargs: Any) -> str:
        """
        Get a translated sentence by ID with optional formatting parameters.

        Args:
            sentence_id: The ID of the sentence to retrieve
            **kwargs: Optional keyword arguments for string formatting

        Returns:
            The formatted translated sentence

        Raises:
            KeyError: If the sentence ID is not found
        """
        return self.sentences[sentence_id].format(**kwargs)

    def __LoadFile(self,
                   file_name: str) -> None:
        """
        Load and parse a translation XML file.

        Args:
            file_name: Path to the XML translation file
        """
        tree = ElementTree.parse(file_name)
        root = tree.getroot()

        for child in root:
            if child.tag == TranslationLoaderConst.SENTENCE_XML_TAG and child.text is not None:
                sentence_id = child.attrib["id"]
                self.sentences[sentence_id] = child.text.replace("\\n", "\n")

                self.logger.GetLogger().debug(
                    f"Loaded sentence '{sentence_id}': {self.sentences[sentence_id]}"
                )

        self.logger.GetLogger().info(
            f"Language file successfully loaded, number of sentences: {len(self.sentences)}"
        )
