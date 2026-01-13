import errno
import logging
import os
import re
import sys
import platform
import traceback
from typing import overload, Literal

#
# Misc utilities
#

def get_variable_name(stack_back=-2):
    """
    Called by .dumper.dumps()

    Pulls the variable names from the function that called this function

    This function traces back through the call stack, so we have to subtract -1
    for every intermediate function, including this function.

    Subtract -1 for every intermediate step in the call stack.
    So we have: -1 for this function -1 for whoever called it = -2, which is the default.

    If there are more functions in the middle then subtract -1 for each of them. For example:
    -1 for this function -1 for dumps(), and -1 for whoever called dumps = -3.

    :param stack_back: How far back we need to go in the stack (see above description)
    :return: Returns the variable name(s)
    """
    stack = traceback.extract_stack()
    caller_name = stack[-2].name
    caller_len = len(caller_name)
    line = stack[stack_back].line
    # Example line: print('fu', 'bar/', argel1200.utilities.dumps(header), '/foobar')
    my_line = re.sub(r'(\s|\u180B|\u200B|\u200C|\u200D|\u2060|\uFEFF)+', '', line)  # Remove all whitespace
    caller_start = my_line.find(caller_name + '(')  # Find where the caller string is (e.g. where "dumps(" starts)
    caller_end = caller_start + caller_len  # And where it ends (the index of the '(' in "dumps("  )
    my_line_substr = my_line[caller_end:]  # Get a substr of everything past the caller (e.g. "dumps").

    # Now let's find all the variable names passed in
    vars_passed_in = []
    parens = 0
    str_start = None
    for idx, char in enumerate(my_line_substr):
        if char == '(':
            parens += 1
            str_start = idx + 1
        elif char == ',' or char == ')':
            vars_passed_in.append(my_line_substr[str_start:idx])
            str_start = idx + 1
            if char == ')':
                parens -= 1
                if parens == 0:
                    break
    return vars_passed_in




#
# Class utilities
#

def import_class_from_string(path, parent_class_name=''):
    """
    Takes a string name of a class and returns an actual instance of that class.
    Useful when you need to (or it's just more elegant to) dynamically determine the class.

    :param path: The full class path.  (For example:  package.module.class)
    :param parent_class_name: Name of the parent class (For example: BaseClass)
    :return: The class, the parent class, or None
    """
    from importlib import import_module
    module_path, _, class_name = path.rpartition('.')
    mod = import_module(module_path)
    try:
        klass = getattr(mod, class_name)
    except:
        if parent_class_name:
            try:
                klass = getattr(mod, parent_class_name)
            except:
                return None
        else:
            return None
    return klass

#
# Logging utilities
#

def add_logging_level(level_name, level_num, method_name=None):
    """
    Dynamically adds a new logging level to the Python logging module.

    :param level_name: Name of the logging level (e.g. 'TRACE', 'MEMDUMP').
    :param level_num: Numeric value of the logging level (e.g. logging.DEBUG - 1 for TRACE).
    :param method_name: The method name to be added to the logging module (e.g. 'trace').
                        If not provided, the lowercase version of level_name will be used.
    """
    # Ensure the level_name is uppercase for the numeric constant
    uppercase_level_name = level_name.upper()

    # Ensure method_name is lowercase, or derive it from level_name
    lowercase_method_name = method_name.lower() if method_name else level_name.lower()

    # Check for conflicts with existing level constants and method names
    if hasattr(logging, uppercase_level_name):
        raise ValueError(f"Logging level '{uppercase_level_name}' already exists")

    if hasattr(logging, lowercase_method_name):
        raise ValueError(f"Logging method '{lowercase_method_name}' already exists")

    # Add the level to the logging module
    logging.addLevelName(level_num, uppercase_level_name)
    setattr(logging, uppercase_level_name, level_num)  # Add the constant in UPPERCASE

    # Define the custom logging methods
    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    # Add the lowercase method for the logger and root logger
    setattr(logging.getLoggerClass(), lowercase_method_name, log_for_level)
    setattr(logging, lowercase_method_name, log_to_root)

# Attept to help Pyrefly not generate warnings.
@overload
def logging_init(return_logger: Literal[True]) -> tuple[logging.Logger, dict[str, int]]: ...

@overload
def logging_init(return_logger: Literal[False] = ...) -> dict[str, int]: ...
def logging_init(return_logger=False):
    """
    Initializes the logging module with custom levels and a default configuration.

    TRACE is for more detail beyond DEBUG
    MEMDUMP for even more detail than TRACE.
    """
    add_logging_level('TRACE', logging.DEBUG - 1)
    add_logging_level('MEMDUMP', logging.DEBUG - 9)
    logging.basicConfig(level=logging.MEMDUMP, format='%(asctime)s - %(levelname)s - %(message)s')

    log_levels = {
        'memdump': logging.MEMDUMP,
        'trace': logging.TRACE,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL,
        }

    if return_logger is True:
        logger = logging.getLogger()
        return (logger, log_levels)
    else:
        return log_levels



def log_or_print(msg, logger=None, level='debug'):
    """
    Logs the message via the supplied logger or prints to console if no logger is provided.
    If the provided logging level is invalid, logs a warning and defaults to 'critical'.

    :param msg: The message to log or print.
    :param logger: Logger instance, optional.
    :param level: Logging level as a string (e.g., 'debug', 'info', 'error').
                  Defaults to 'debug'.
    """
    if logger:
        # Check if the provided logging level is valid
        if hasattr(logger, level):
            log_method = getattr(logger, level)
            log_method(msg)
        else:
            # Log a message indicating the issue and fall back to critical
            logger.error(f"Invalid logging level '{level}' passed to log_or_print. Falling back to 'critical'.")
            logger.critical(msg)
    else:
        print(msg)


#
# File utilities
#

def open_file(filename, mode='r', newline='', encoding='utf-8', logger=None):
    """
    Opens a file, with some error handling and enhanced functionality for permission checking.
    :param encoding: Encoding used by the file
    :param filename: The name of the file to pass to open()
    :param mode: The read/write mode to pass to open()
    :param newline: The newline to pass to open()
    :param logger: Optional instance of the logging module
    :return: The file handle (or it exits if there is an error)
    """

    # Step 1: Check permissions or file existence
    try:
        if not os.path.exists(filename):
            # Skip access check if file doesn't exist and mode allows writing
            if 'w' in mode or 'a' in mode:
                pass  # File creation is allowed in these modes
            else:
                raise FileNotFoundError(f"ERROR: Cannot read ({mode}) {filename} because it does not exist.")
        else:
            # Check access if the file exists
            access_mode = os.R_OK if 'r' in mode else os.W_OK
            if not os.access(filename, access_mode):
                raise PermissionError(f"ERROR: Insufficient permissions to access {filename} in mode {mode}.")
    except FileNotFoundError as err:
        log_or_print(f"ERROR: {err}", logger=logger, level='critical')
        sys.exit(1)
    except PermissionError as err:
        log_or_print(f"ERROR: {err}", logger=logger, level='critical')
        sys.exit(1)
    except Exception as err:
        log_or_print(
            f"ERROR: Unexpected error occurred while checking permissions for {filename}: {repr(err)}",
            logger=logger,
            level='critical'
            )
        sys.exit(1)

    # Step 2: Try to open the file
    try:
        if mode == 'rb' or mode == 'wb':  # Binary mode
            file_handle = open(filename, mode)
        else:
            file_handle = open(filename, mode, newline=newline, encoding=encoding)
    except FileNotFoundError:
        log_or_print(f"ERROR: File {filename} not found. Aborting.", logger=logger, level='critical')
        sys.exit(1)
    except PermissionError:
        if platform.system() == 'Windows':  # Windows-specific locking warning
            log_or_print(
                f"ERROR: File {filename} might be open in another application or locked on Windows.",
                logger=logger,
                level='critical'
                )
        else:
            log_or_print(f"ERROR: Permission error accessing {filename}.", logger=logger, level='critical')
        sys.exit(1)
    except OSError as err:
        error_details = errno.errorcode.get(err.errno, "Unknown error")
        log_or_print(
            f"ERROR: Cannot open file {filename}; mode: {mode}; (OSError.errno: {err.errno}; message: {error_details}); Exception: {repr(err)}",
            logger=logger,
            level='critical'
            )
        sys.exit(os.EX_OSFILE)
    except Exception as err:
        log_or_print(f"ERROR: Unexpected error occurred while opening {filename}: {repr(err)}", logger=logger,
                     level='critical')
        sys.exit(1)

    # Return the open file handle
    return file_handle
