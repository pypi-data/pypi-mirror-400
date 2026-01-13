#############################
###                       ###
###    Epitech Console    ###
###  ----__init__.py----  ###
###                       ###
###=======================###
### by JARJARBIN's STUDIO ###
#############################


from epitech_console.System.time import Time
from epitech_console.System.stopwatch import StopWatch
from epitech_console.System.config import Config
from epitech_console.System.console import Console
from epitech_console.System.log import Log
from epitech_console.System.setting import Setting
from epitech_console.System.action import Action, Actions

from sys import stdin, stdout, stderr


__all__ : list[str] = [
    'Time',
    'StopWatch',
    'Config',
    'Console',
    'Log',
    'Action',
    'Actions',
    'Setting',
    'stdin',
    'stdout',
    'stderr',
]


__author__ : str = 'Nathan Jarjarbin'
__email__ : str = 'nathan.amaraggi@epitech.eu'
