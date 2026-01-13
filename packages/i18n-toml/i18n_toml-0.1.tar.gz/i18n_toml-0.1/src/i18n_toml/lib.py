"""
i18-toml library main module.
"""

import warnings
import tomllib
from pathlib import Path

class I18nToml:
    """
    Main class for the i18n-toml library.
    """

    def __init__(self, folder: Path, locale: str):
        """
        Init I18nToml object.
        
        :param folder: Folder with locales.
        :type folder: pathlib.Path
        :raises NotADirectoryError: If the locale folder does not exist.
        :warns UserWarning: If the locale folder is empty.
        """
        self._locale = locale
        self._folder = folder / locale
        # Check if the folder exists and not empty
        if not self._folder.is_dir():
            raise NotADirectoryError(f"Locale folder `{self._folder}` does not exist.")
        if not any(self._folder.iterdir()):
            warnings.warn(f"Locale folder `{self._folder}` is empty.")



    def __call__(self, key: str) -> str:
        """
        Get localized text by key (dubles of get() method)
        
        :param key: Key to get text from.
        :type key: str
        :return: Text.
        :rtype: str
        :raises FileNotFoundError: If the file with the key does not exist.
        """
        return self.get(key)



    def get(self, key: str) -> str:
        """
        Get localized text by key.
        
        :param key: Key to get text from.
        :type key: str
        :return: Text.
        :rtype: str
        :raises FileNotFoundError: If the file with the key does not exist.
        """
        key_parts = key.split(".")
        file_name = key_parts[0] + ".toml"
        file_path = self._folder / file_name
        try:
            with open(file_path, "rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"File `{file_path}` does not exist.") from None
        # Go through keys hierarchy until last key and get the value
        value = data
        for part in key_parts[1:]:
            try:
                value = value[part]
            except KeyError:
                raise KeyError(f"Key `{part}` not found in `{file_path}`.") from None
        return str(value)
