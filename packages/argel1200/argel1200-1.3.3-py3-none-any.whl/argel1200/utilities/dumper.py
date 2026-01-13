from .utilities import get_variable_name
import dumper

def dumps(*items):
    """
    Front end to dumper.dumps that does some helpful things like
    finding the variable names and adding them to the output string
    """
    dumper.max_depth = 10
    item_names = get_variable_name(-3)
    ret_str = ""
    for idx, item in enumerate(items):
        if idx > 0:
            ret_str += f"\n"
        item_name = item_names[idx]
        ret_str += f"'{item_name}' = "
        ret_str += dumper.dumps(item)  # string version of dump
    return ret_str
