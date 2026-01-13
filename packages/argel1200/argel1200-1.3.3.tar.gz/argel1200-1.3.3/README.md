# argel1200.utilities
A small collection of utility functions that help reduce boilerplate code.

Version 1.3.0+ now spreads dependencies across files, so you can use e.g., open_file without having click and 
dumper installed.

## Dumper Utilties

### dumps
Wrapper for dumper, to make it eaier to get Perl style Data Dumper output. Assumes you want strings back, and leverages get_variable_name to pull the calling function.

#### get_variable_name

Helper function used by dumps. Perl's Data::Dumper gives variable_name=value output. This seeks to mimic that.

## Class Utilties 

### import_class_from_string
Useful when you need to (or it's just more elegant to) dynamically determine the class based on a string that you are obtaining dynamically at runtime. Useful if you have a base class and multiple subclasses. Very useful if you want to build out your classes as needed (something can just be a base class now, then later on you could create a sub class for it and your script will start loading it as the new sub class automatically)

## Logging Utilties

### add_logging_level

Add custom logging levels

### logging_init
Uses haggis.logs to add two additional "debug" logging levels: 'TRACE' and 'MEMDUMP' and initializes a logging instance if return_logger is True.

### log_or_print

Streamlines if logger log.level else print workflows.

## File Utilities

### open_file
Wrapper for opening a file that provides basic error handling. Get those try blocks out of _your_ script!

## Command-line Utilties

### process_cli_using_click
Useful if you want to use click in standalone=False mode. 
Provides basic error handling (required for standalone=False)

---

# History
## 1.3.0
- Restructured so that people can use e.g. open_file without having to install click or dumper.
-- Pulling some tricks in utilities/__init__.py to maintain backwards compatibility.
## 1.2.0 
- Added my own add_log_level that supports Python 3.13. Used to use Haggis for this, but it's using old methods that no longer work.
- Improved open_file to check for permissions and tries to catch if a file is open on Windows
- Added log_or_print