#############################
###                       ###
###    Epitech Console    ###
###  ----__init__.py----  ###
###                       ###
###=======================###
### by JARJARBIN's STUDIO ###
#############################


from builtins import object
from typing import Any

from epitech_console import Animation, ANSI, Error, System, Text


__version__ : str = 'v0.1.8'
__author__ : str = 'Nathan Jarjarbin'
__email__ : str = 'nathan.amaraggi@epitech.eu'


def _banner(
    ) -> None:
    """
        Show a simple banner.
    """

    banner_size = 50

    epitech = ANSI.Color.epitech_fg()
    epitech_dark = ANSI.Color.epitech_dark_fg()
    reset = ANSI.Color.color(ANSI.Color.C_RESET)

    offset_t = Text.Text("  ")
    title_t = epitech + Text.Text(f'{System.Setting.S_PACKAGE_NAME}').bold().underline() + reset + "  " + Text.Text.url_link(
        "https://github.com/Jarjarbin06/epitech_console", text="repository")
    version_t = Text.Text(" " * (10 - len(System.Setting.S_PACKAGE_VERSION))) + epitech_dark + Text.Text("version ").italic() + Text.Text(
        f'{System.Setting.S_PACKAGE_VERSION}').bold() + reset
    desc_t = Text.Text("   Text • Animation • ANSI • Error • System   ").italic()
    line_t = epitech + ("─" * banner_size) + reset

    System.Console.print(line_t, offset_t + title_t + " " + version_t + offset_t, offset_t + desc_t + offset_t, line_t, separator="\n")


def init(
        banner: bool | None = None,
    ) -> None:
    """
        init() initializes the epitech console package and show a banner (if SETTING : show-banner = True in config.ini)

        Parameters:
            banner (bool | None, optional) : Override the show-banner setting
    """

    try:
        if (System.Setting.S_SETTING_SHOW_BANNER and banner is None) or banner == True:
            _banner()
        System.Setting.update()
        Animation.BasePack.update()
        ANSI.BasePack.update()
        System.Setting.S_LOG_FILE.log("INFO", "module", "epitech_console initialized")

    ## cannot be tested with pytest ##

    except Error.Error as error: # pragma: no cover
        print(error) # pragma: no cover
        print(Error.Error._lauch_error()) # pragma: no cover

    except Exception as error: # pragma: no cover
        print(f"\033[101m \033[0m \033[91m{error}\033[0m") # pragma: no cover
        print(
            "\033[103m \033[0m \033[93mepitech_console launched with error\033[0m\n"
            "\033[103m \033[0m\n"
            "\033[103m \033[0m \033[93mPlease reinstall with :\033[0m\n"
            "\033[103m \033[0m \033[93m    'pip install --upgrade --force-reinstall epitech_console'\033[0m\n"
            "\033[103m \033[0m\n"
            "\033[103m \033[0m \033[93mPlease report the issue here : https://github.com/Jarjarbin06/epitech_console/issues\033[0m\n"
        ) # pragma: no cover


def quit(
        *,
        show : bool = False,
        delete_log: bool = False
    ) -> None:
    """
        quit() uninitializes the epitech console package

        Parameters:
            show (bool, optional) : show the log file on terminal
            delete_log (bool, optional) : delete the log file
    """

    if System.Setting.S_SETTING_LOG_MODE:
        System.Setting.S_LOG_FILE.log("INFO", "module", "epitech_console uninitialized")
        System.Setting.S_LOG_FILE.close()
        System.Setting.S_CONFIG_FILE.set("SETTING", "opened-log", "null")

        ## cannot be tested with pytest ##

        if show:
            System.Console.print(str(System.Setting.S_LOG_FILE)) # pragma: no cover

        if delete_log:
            System.Setting.S_LOG_FILE.close(delete=True)


__all__ : list[str] = [
    'Animation',
    'ANSI',
    'Error',
    'System',
    'Text',
    'init',
    'quit',
    '__version__',
    '__author__',
    '__email__'
]

init(banner=False)
quit(delete_log=True)
