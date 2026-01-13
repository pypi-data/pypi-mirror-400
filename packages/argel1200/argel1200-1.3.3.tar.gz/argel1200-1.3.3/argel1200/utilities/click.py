import click
import sys

def process_cli_using_click(my_cli):
    """
    Because we are *not* using click's standalone mode, we need to do our own error handling.
    This function takes care of that.

    :param my_cli:  The function you defined via click to process the command line arguments
    """
    click_invoke_rc = None

    try:
        click_invoke_rc = my_cli(standalone_mode=False)
    except click.exceptions.NoSuchOption as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"Invalid option detected:")
        print(f"Type: {exc_type}; Value: {exc_value}; Traceback: {exc_traceback}")
        print(f"Try running the program with -h or --help.")
        exit(3)
    except click.exceptions.UsageError as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"A usage error occurred:")
        print(f"Type: {exc_type}; Value: {exc_value}; Traceback: {exc_traceback}")
        print(f"Try running the program with -h or --help.")
        exit(5)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print(f"An unexpected command line processing error occurred:")
        print(f"Type: {exc_type}; Value: {exc_value}; Traceback: {exc_traceback}")
        print(f"Try running the program with -h or --help.")
        exit(10)

    if click_invoke_rc == 0:  # Catch if -h, --help, --version, or something unknown was specified
        exit(1)