# -*- python -*-
# -*- coding: utf-8 -*-
#
#       dxtr.utils.logging
#
# This submodule sets the logging parameters of the library.
# It also contains two logging-related decorators:
# * one that checks if pyvista (optional dependency) is installed
# * one that checks it the first argument of a function is of the expected type.
#
#       File author(s):
#           Olivier Ali <olivier.ali@inria.fr>
#
#       File contributor(s):
#           Olivier Ali <olivier.ali@inria.fr>
#           Jonathan Legrand <jonathan.legrand@ens-lyon.fr>
#
#       File maintainer(s):
#           Olivier Ali <olivier.ali@inria.fr>
#
#       Copyright © by Inria
#       Distributed under the LGPL License..
#       See accompanying file LICENSE.txt or copy at
#           https://www.gnu.org/licenses/lgpl-3.0.en.html
#
# -----------------------------------------------------------------------
from __future__ import annotations
from functools import wraps
from typing import Optional, Any
import logging
from logging import handlers # Need to do that because bug in the test otherwise...
from logging import _nameToLevel as LEVEL
from pathlib import Path
import time
import sys
import os

DEFAULT_LOG_LEVEL_CNSL = 'INFO'
DEFAULT_LOG_LEVEL_FILE = 'DEBUG'
LOG_FMT_CNSL = "{name}.{module:<25} | {levelname}: {message}"
LOG_FMT_FILE = "{name}.{module:<25} | -l.{lineno}- {levelname}: {message}"
FORMATTER_CNSL = logging.Formatter(LOG_FMT_CNSL, style='{')
FORMATTER_FILE = logging.Formatter(LOG_FMT_FILE, style='{')

def get_console_handler() -> logging.StreamHandler:
    """Instanciates the logging output on the console.
    """
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER_CNSL)
    return console_handler


def get_file_handler(log_file:str,
                     log_level:str=DEFAULT_LOG_LEVEL_FILE,
                     time_rotating:bool=True,
                     ) -> logging.FileHandler:
    """Instanciate the logging output written on disk.
    
    Parameters
    ----------
    log_file
        The file where to store the log.
    log_level
        The log level to save on file.
    time_rotating
        If True, a time-rotating managment of log files is set.
    
    Returns
    -------
    file_handler
        The object that manages all the log messages.
    
    Notes
    -----
      * If time-rotation is used
        * One file is generated per day, starting at midnight.
        * At most, 5 files are stored on disk. Meaning that we conserve at
          most a week of log.
    """

    if time_rotating:
        file_handler = handlers.TimedRotatingFileHandler(
            log_file, when='midnight', backupCount=5)
    else:
        file_handler = logging.FileHandler(log_file, mode='w')

    file_handler.setFormatter(FORMATTER_FILE)
    file_handler.setLevel(log_level)
    return file_handler


def get_logger(logger_name:str, log_file:Optional[str]=None, 
               log_level=DEFAULT_LOG_LEVEL_CNSL) -> logging.Logger:
    """Instanciates the two logging outputs: console & file on disk.

    Parameters
    ----------
    logger_name
        The name given to the created Logger object.
    
    log_file 
        Optional, default is None. The path to the file where to write the log.
    
    log_level
        Optional, default is 'INFO'. The log level for the console output.
    
    Returns
    -------
        The Logger object gathering all the info.
    """

    if log_file is None:
        here = os.getcwd()
        name = '.'.join([logger_name, 'log'])
        log_file = '/'.join([here, name])

    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(log_file, log_level))

    logger.propagate = False

    return logger


# ################### #
# Instantiates logger #
# ################### #

here = Path(os.path.dirname(__file__))
root = list(here.parents)[2]
log_path = root.joinpath('log/')

if not log_path.is_dir():
    log_path.mkdir() 

time_stamp = time.strftime("%y%m%d")
file_name = '.'.join((time_stamp, 'log'))
log_file = log_path.joinpath(file_name)
logger = get_logger('dxtr', log_file=log_file)

# ################# #
# Useful decorators #
# ################# #

def require_pyvista(func) -> Optional[Any]:
    """Checks if the library pyvista is installed.

    Notes
    -----
      * This library is an optional dependency.
      * It is used in the visu and io modules.
      * In the io module it is required for recording `Cochain`.
      * The dependency to logger does not seem super clean... 
        Maybe this means that this decorator does not belong here...
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            import pyvista as pv 
            return func(*args, **kwargs)
        except ImportError:
            from dxtr import logger
            logger.warning('Pyvista not installed', ImportWarning)
            return None
    return wrapper


def mutelogging(func) -> Any:
    """Increases momentary the logging level so no info are displayed.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        from dxtr import logger
        
        initial_logging_level = logger.level
        logger.setLevel(LEVEL['ERROR'])
        
        result = func(*args, **kwargs)
        
        logger.setLevel(initial_logging_level)
        
        return result
    
    return wrapper
