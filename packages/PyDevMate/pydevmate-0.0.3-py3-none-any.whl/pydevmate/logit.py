#!/usr/bin/env python 
# -*- coding: utf-8 -*-

import logging
import os
from typing import Optional
from termcolor import colored
from pydevmate.colors import Colors
from pydevmate.infos import Infos

class LogIt(logging.Logger):
    
    """
    A helper class to create and configure loggers.
    """

    def __init__(
        self, 
        name: Optional[str] = None, 
        level: Optional[int] = None, 
        console: bool = True, 
        file: bool = False, 
        format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ):
        """
        Initialize the logger with the specified configuration.
        Args:
            name (str, optional): Name of the logger. Defaults to module name if not provided.
            level (int, optional): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            console (bool): If True, logs to the console.
            file (bool): If True, logs to a file named 'logit.log'.
            format (str): Format of the log message.
        """
        
        # Parent class initialization
        super().__init__(name)
        
        # Check if name is provided
        if name is None:
            # Get executed script name
            name = Infos.get_script_package_name()
        
        # Check if LogIt directory exists
        self.setLevel(level if level else logging.INFO)
        self.propagate = False  # Avoid duplicate logs

        # Check if handlers are already added
        if not self.hasHandlers():
            formatter = logging.Formatter(format)

            # Add console handler
            if console:
                self._add_console_handler(formatter)

            # Add file handler
            if file:
                self._add_file_handler(formatter)

    def _add_console_handler(self, formatter: logging.Formatter):
        """
        Add a console handler to the logger.
        Args:
            formatter (logging.Formatter): Formatter for the handler.
        """
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.addHandler(console_handler)

    def _add_file_handler(self, formatter: logging.Formatter):
        """
        Add a file handler to the logger.
        Args:
            formatter (logging.Formatter): Formatter for the handler.
        """
        directory = '__logit__'
        if not os.path.exists(directory):
            os.makedirs(directory)
        try:
            file_handler = logging.FileHandler(os.path.join(directory, 'logit.log'))
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to create file handler: {e}")
    
    def debug(self, message: str, *args, color: Colors = Colors.CYAN, attrs=[], **kwargs) -> None:
        """
        Log a debug message.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger.
        """
        if args:
            message = message % args
        super().debug(colored(message, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]), **kwargs)
        
    def info(self, message: str, *args, color: Colors = Colors.WHITE, attrs: list = [], **kwargs) -> None:
        """
        Log an info message.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger.
        """
        if args:
            message = message % args
        super().info(colored(message, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]), **kwargs)
        
    def success(self, message: str, *args, color: Colors = Colors.GREEN, attrs: list = [], **kwargs) -> None:
        """
        Log a success message.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger.
        """
        if args:
            message = message % args
        self.info(colored(message, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]), **kwargs)
        
    def show(self, message: str, *args, color: Colors = Colors.LIGHT_BLUE, attrs: list = [Colors.BOLD], **kwargs) -> None:
        """
        Log a show message.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger.
        """
        if args:
            message = message % args
        # Get .value of each attrs element if it is a Colors enum
        self.info(colored(message, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]), **kwargs)
    
    def warning(self, message: str, *args, color: Colors = Colors.YELLOW, attrs: list = [], **kwargs) -> None:
        """
        Log a warning message.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger.
        """
        if args:
            message = message % args
        super().warning(colored(message, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]), **kwargs)
        
    def warn(self, message: str, *args, color: Colors = Colors.YELLOW, attrs: list = [], **kwargs) -> None:
        """
        Alias for warning.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger.
        """
        self.warning(message, *args, color=color, attrs=attrs, **kwargs)
        
    def error(self, message: str, *args, color: Colors = Colors.RED, attrs: list = [], **kwargs) -> None:
        """
        Log an error message.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger.
        """
        if args:
            message = message % args
        super().error(colored(message, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]), **kwargs)
        
    def critical(self, message: str, *args, color: Colors = Colors.MAGENTA, attrs: list = [], **kwargs) -> None:
        """
        Log a critical message.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger.
        """
        if args:
            message = message % args
        super().critical(colored(message, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]), **kwargs)
        
    def exception(self, message: str, *args, color: Colors = Colors.RED, attrs: list = [], **kwargs) -> None:
        """
        Log an exception message.
        Args:
            message (str): The message to log (supports % formatting).
            *args: Arguments for string formatting.
            color (Colors): The color of the message.
            attrs (list): Text attributes.
            **kwargs: Additional keyword arguments passed to parent logger (e.g., exc_info).
        """
        if args:
            message = message % args
        super().exception(colored(message, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]), **kwargs)
        
    def separator(self, size: int = 100, color: Colors = Colors.WHITE, attrs=['bold']) -> None:
        """
        Log a separator.
        Args:
            size (int): The size of the separator.
            color (Colors): The color of the separator.
            attrs (list): The attributes of the separator.
        """
        self.info(colored('-' * size, color.value, attrs=[attr.value for attr in attrs if isinstance(attr, Colors)]))
        
    def line_break(self, nb_breaks: int = 1) -> None:
        """
        Log a line break.
        Args:
            nb_breaks (int): Number of line
        """
        for _ in range(nb_breaks):
            self.info('')
        

# Main function to test the decorator
if __name__ == '__main__':
    
    # Usage
    logger = LogIt(level=logging.DEBUG, console=True, file=True)
    
    # Test the logger
    logger.separator()
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
    logger.exception("This is an exception message.")
    logger.separator(100)
    logger.line_break()
    logger.separator(50)
    logger.line_break(2)
    logger.separator(25)
    logger.line_break(3)
    logger.separator(10)