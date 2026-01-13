#############################
###                       ###
###    Epitech Console    ###
###   ----setting.py----  ###
###                       ###
###=======================###
### by JARJARBIN's STUDIO ###
#############################


from builtins import object
from typing import Any


class Setting:
    """
        Setting class.

        All module's settings imported.

        Attributes:
            S_OS (str): os mode.

            S_CONFIG_FILE (Config | None): module's config file.
            S_LOG_FILE (Log | None): log file.

            S_PACKAGE_NAME (str): package name.
            S_PACKAGE_VERSION (str): package version.
            S_PACKAGE_DESCRIPTION (str): package description.
            S_PACKAGE_REPOSITORY (str): package repository url.

            S_SETTING_SHOW_BANNER (bool): show banner.
            S_SETTING_AUTO_COLOR (bool): auto color.
            S_SETTING_SAFE_MODE (bool): safe mode.
            S_SETTING_MINIMAL_MODE (bool): minimal mode.
            S_SETTING_DEBUG_MODE (bool): debug mode.
            S_SETTING_LOG_MODE (bool): log mode.
    """


    from epitech_console.System.log import Log
    from epitech_console.System.config import Config


    S_OS : str | None = None

    S_CONFIG_FILE : Config | None = None
    S_LOG_FILE : Log | None = None

    S_PACKAGE_PATH : str = "null"
    S_PACKAGE_NAME : str = "null"
    S_PACKAGE_VERSION : str = "null"
    S_PACKAGE_DESCRIPTION : str = "null"
    S_PACKAGE_REPOSITORY : str = "null"

    S_SETTING_SHOW_BANNER : bool = False
    S_SETTING_AUTO_COLOR : bool = False
    S_SETTING_SAFE_MODE : bool = True
    S_SETTING_MINIMAL_MODE : bool = True
    S_SETTING_DEBUG_MODE : bool = False
    S_SETTING_LOG_MODE : bool = False
    S_SETTING_OPENED_LOG : str = "null"


    @staticmethod
    def update(
        ) -> None:
        """
            Initialize the BasePack class
        """

        from platform import system
        from epitech_console.System.config import Config
        from epitech_console.System.log import Log
        from epitech_console.Error.error import ErrorSetting

        Setting.S_OS = system()

        if Setting.S_OS == "Windows":
            Setting.S_PACKAGE_PATH = __file__.removesuffix("System\\setting.py")

        elif Setting.S_OS == "Linux":
            Setting.S_PACKAGE_PATH = __file__.removesuffix("System/setting.py")

        else:
            Setting.S_PACKAGE_PATH = __file__.removesuffix("System/setting.py").removesuffix("System\\setting.py")

        Setting.S_CONFIG_FILE = Config(Setting.S_PACKAGE_PATH)

        Setting.S_PACKAGE_NAME = Setting.S_CONFIG_FILE.get("PACKAGE", "name")
        Setting.S_PACKAGE_VERSION = Setting.S_CONFIG_FILE.get("PACKAGE", "version")
        Setting.S_PACKAGE_DESCRIPTION = Setting.S_CONFIG_FILE.get("PACKAGE", "description")
        Setting.S_PACKAGE_REPOSITORY = Setting.S_CONFIG_FILE.get("PACKAGE", "repository")

        Setting.S_SETTING_SHOW_BANNER = Setting.S_CONFIG_FILE.get_bool("SETTING", "show-banner")
        Setting.S_SETTING_AUTO_COLOR = Setting.S_CONFIG_FILE.get_bool("SETTING", "auto-color")
        Setting.S_SETTING_SAFE_MODE = Setting.S_CONFIG_FILE.get_bool("SETTING", "safe-mode")
        Setting.S_SETTING_MINIMAL_MODE = Setting.S_CONFIG_FILE.get_bool("SETTING", "minimal-mode")
        Setting.S_SETTING_DEBUG_MODE = Setting.S_CONFIG_FILE.get_bool("SETTING", "debug")
        Setting.S_SETTING_LOG_MODE = Setting.S_CONFIG_FILE.get_bool("SETTING", "log")

        if Setting.S_SETTING_LOG_MODE:
            Setting.S_SETTING_OPENED_LOG = Setting.S_CONFIG_FILE.get("SETTING", "opened-log")

            if Setting.S_SETTING_OPENED_LOG == "null":
                Setting.S_LOG_FILE = Log(Setting.S_PACKAGE_PATH + "log")
                Setting.S_CONFIG_FILE.set("SETTING", "opened-log", Setting.S_LOG_FILE.log_file_name)
                Setting.S_SETTING_OPENED_LOG = Setting.S_CONFIG_FILE.get("SETTING", "opened-log")

            else:
                Setting.S_LOG_FILE = Log(Setting.S_PACKAGE_PATH + ("log\\" if system() == "Windows" else "log/"), file_name=Setting.S_SETTING_OPENED_LOG)

            if Setting.S_LOG_FILE is None:
                print('\x1b[101 \x1b[0m \x1b[91mAn error occured when updating setting S_LOG_FILE (currently equal \"None\"\x1b[0m')
            Setting.S_LOG_FILE.log("INFO", "function", "System.Setting.update(): setting updated")
