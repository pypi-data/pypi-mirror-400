#############################
###                       ###
###    Epitech Console    ###
###     ----log.py----    ###
###                       ###
###=======================###
### by JARJARBIN's STUDIO ###
#############################


from builtins import object
from typing import Any


class Log:
    """
        Log class.

        Log file tool.
    """


    def __init__(
            self,
            path : str,
            file_name : str | None = None
        ) -> None:
        """
            Log class constructor.

            Parameters:
                path (str): path to log file
                file_name (str | None, optional): name of log file
        """

        from datetime import datetime
        from platform import system
        from epitech_console.Error.error import Error, ErrorLog

        self.log_path : str = (path if path[-1] in ["/", "\\"] else path + ("\\" if system() == "Windows" else "/"))
        self.log_file_name : str = str(datetime.now()).replace(":", "_") if not file_name else file_name

        try :
            open(f"{self.log_path}{self.log_file_name}.log", 'x').close()

            with open(f"{self.log_path}{self.log_file_name}.log", 'a') as log_file:
                log_file.write("   date          time      | [TYPE]  title      | detail\n\n---START---")
            log_file.close()


        ## cannot be tested with pytest ##

        except FileNotFoundError: # pragma: no cover
            raise ErrorLog("failed to create log file") # pragma: no cover

        except FileExistsError:
            pass

        try :
            with open(f"{self.log_path}{self.log_file_name}.log", 'r') as log_file:
                string = log_file.read()
            log_file.close()

            assert "   date          time      | [TYPE]  title      | detail\n\n---START---" in string

        ## cannot be tested with pytest ##

        except FileNotFoundError or AssertionError: # pragma: no cover
            raise ErrorLog("failed to write on log file") # pragma: no cover


    def log(
            self,
            status : str,
            title : str,
            description : str
        ) -> None:
        """
            Format a log message then save it.

            Parameters:
                status (str): log status
                title (str): log title
                description (str): log description
        """

        from datetime import datetime

        status = f"[{status}]"
        status += " " * (7 - len(status))
        status = status[:7]
        title += " " * (10 - len(title))
        title = title[:10]

        log_time : str = str(datetime.now())
        log_str : str = f"{log_time} | {status} {title} | {description}"

        self.save(log_str)


    def comment(
            self,
            comment : str
        ) -> None:
        """
            Save a comment in the log file.

            Parameters:
                comment (str): comment
        """

        self.save(f">>> {comment}")


    def save(
            self,
            log_str : str
        ) -> None:
        """
            Save a new log in the log file.

            Parameters:
                log_str (str): log string
        """

        from epitech_console.Error.error import ErrorLog

        try :
            with open(f"{self.log_path}{self.log_file_name}.log", 'a') as log_file :
                log_file.write(f"\n{log_str}")
            log_file.close()

        ## cannot be tested with pytest ##

        except FileNotFoundError: # pragma: no cover
            raise ErrorLog("failed to write on log file") # pragma: no cover


    def close(
            self,
            *,
            delete : bool = False
        ) -> None :
        """
            Close the log file.

            Parameters:
                delete (bool, optional): delete the log file
        """

        from epitech_console.Error.error import ErrorLog

        try:
            with open(f"{self.log_path}{self.log_file_name}.log", 'a') as log_file :
                log_file.write(f"\n----END----\n")
            log_file.close()

        ## cannot be tested with pytest ##

        except FileNotFoundError: # pragma: no cover
            raise ErrorLog("failed to write on log file") # pragma: no cover

        if delete :
            self.delete()


    def delete(
            self
        ) -> None:
        """
            Delete the log file.
        """

        from os import remove
        from epitech_console.Error.error import ErrorLog

        try:
            remove(f"{self.log_path}{self.log_file_name}.log")

        ## cannot be tested with pytest ##

        except FileNotFoundError: # pragma: no cover
            raise ErrorLog("failed to delete log file") # pragma: no cover


    def read(
            self
        ) -> str :
        """
            Read the log file and returns its content.

            Returns:
                str: content of the log file
        """

        from epitech_console.Error.error import ErrorLog

        log_str : str = ""

        try:
            with open(f"{self.log_path}{self.log_file_name}.log", 'r') as log_file:
                log_str = log_file.read()
            log_file.close()

        ## cannot be tested with pytest ##

        except FileNotFoundError: # pragma: no cover
            raise ErrorLog("failed to read log file") # pragma: no cover

        return log_str


    def __str__(
            self
        ) -> str :
        """
            Returns a formated log file.
        """

        from epitech_console.System import Console
        from epitech_console.ANSI import BasePack, Color

        log_str = self.read()

        color_dict: dict = {
            "[INFO] " : BasePack.P_INFO,
            "[VALID]" : BasePack.P_VALID,
            "[WARN] " : BasePack.P_WARNING,
            "[ERROR]" : BasePack.P_ERROR,
        }
        c_reset : Any = Color.color(Color.C_RESET)
        c_under : Any = Color.color(Color.C_UNDERLINE)
        c_bold : Any = Color.color(Color.C_BOLD)
        start : int = log_str.index("---START---\n") + len("---START---\n")
        end : int = log_str.index("----END----\n")
        logs : list = [lines.split(" | ") for lines in log_str[start:end].splitlines()]
        t_size = len(Console)
        footer : str = f"{c_under}{BasePack.P_INFO[0]}|{c_reset}{c_bold}{c_under}"
        detail_size : int
        string : str = ""

        string += f"{c_under}{BasePack.P_INFO[0]}|{c_reset}{c_bold}{c_under}    date          time      | {c_reset}{c_under}{BasePack.P_INFO[0]}[TYPE] {c_reset}{c_bold}{c_under} title      | detail" + (" " * (t_size - 58)) + f"{c_reset}\n"
        string += f"{BasePack.P_INFO[0]}|{c_reset}{c_bold}" + (" " * (t_size - 1)) + f"{c_reset}\n"

        for log_line in logs :
            if log_line[0][:3] == ">>>" :
                string += f"{BasePack.P_INFO[0]}>>>{c_reset} {BasePack.P_INFO[1]}{log_line[0][3:]}{c_reset}\n"

            else :
                if len(log_line) == 3 and log_line[1][:7].upper() in color_dict :
                    color = color_dict[log_line[1][:7].upper()]
                    string += (
                        f"{color[0]}|{c_reset} " +
                        f"{color[1]}{log_line[0]}{c_reset} | " +
                        f"{color[0]}{log_line[1][0:7]}{c_reset} " +
                        f"{color[1]}{c_bold}{log_line[1][8:]}{c_reset} | " +
                        (f"{log_line[2][:(t_size - 1)]}..." if len(log_line[2]) > (t_size - 1) else f"{color[1]}{log_line[2]}") +
                        f"{c_reset}\n")

                ## cannot be tested with pytest ##

                elif len(log_line) == 1: # pragma: no cover
                    string += f"{Color.color(Color.C_BG_DARK_BLUE)}|{c_reset} " + f"{Color.color(Color.C_FG_DARK_BLUE)}UNFORMATTED\n\"{log_line[0]}\"{c_reset}\n" # pragma: no cover

        string += footer + (" " * (t_size - 1)) + f"{c_reset}\n"

        return string


    def __repr__(
            self
        ) -> str:
        """
            Convert Log object to string.

            Returns:
                str: Log string
        """

        return f"Log(\"{self.log_path}\", \"{self.log_file_name}\")"
