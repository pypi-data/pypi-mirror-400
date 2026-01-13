argel1200
=========

argel1200.utilities
-------------------

A small collection of utility functions that help reduce boilerplate code.

Dumper utilities
~~~~~~~~~~~~~~~

dumps
^^^^^

Wrapper for dumper, to make it easier to get Perl style Data Dumper output. Assumes you want strings back, and leverages get_variable_name to pull the calling function.

get_variable_name
"""""""""""""""""

Helper function used by dumps. Perl's Data::Dumper gives variable_name=value output. This seeks to mimic that.

Class utilities
~~~~~~~~~~~~~~~

import_class_from_string
^^^^^^^^^^^^^^^^^^^^^^^^

Useful when you need to (or it's just more elegant to) dynamically determine the class based on a string that you are obtaining dynamically at runtime. Useful if you have a base class and multiple subclasses. Very useful if you want to build out your classes as needed (something can just be a base class now, then later on you could create a sub class for it and your script will start loading it as the new sub class automatically)

Logging utilities
~~~~~~~~~~~~~~~~~

add_logging_level
^^^^^^^^^^^^^^^^^

Add custom logging levels

logging_init
^^^^^^^^^^^^

Uses add_log_level to add two additional "debug" logging levels: 'TRACE' and 'MEMDUMP' and initializes a logging instance if return_logger is True.

log_or_print
^^^^^^^^^^^^
Streamlines  if logger log.level else print  workflows.

File utilities
~~~~~~~~~~~~~~

open_file
^^^^^^^^^

Wrapper for opening a file that provides basic error handling. Get those try blocks out of _your_ script!

Command-line utilities
~~~~~~~~~~~~~~~~~~~~~~

process_cli_using_click
^^^^^^^^^^^^^^^^^^^^^^^

Useful if you want to use click in standalone=False mode. Provides basic error handling (required for standalone=False)