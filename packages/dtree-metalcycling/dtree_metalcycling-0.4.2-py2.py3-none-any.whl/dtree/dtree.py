"""
Linux 'tree' but for Python dictionaries
"""

# %% Modules

from colorama import Fore
from omegaconf import OmegaConf
from omegaconf.dictconfig import DictConfig

# %% Global variables

BRANCH    = "├── "
SEPARATOR = "│   "
CLOSING   = "└── "
SPACING   = "    "
TEMP = None

# %% Modules

def dtree(dictionary, node_name=None, max_depth=None, print_datatypes=True, print_objects=False, depth=0, fill=""):
    """
    Prints the tree representation of a dictionary and its children

    Input parameters:
    - dictionary <dict> (needed): Dictionary to be used to create the tree
    - node_name <str> (optional): Name of the dictionary to be used as the root node
    - max_depth <int> (optional): Maximum depth of the tree to be printed (e.g., 'max_depth = 0' only prints the root, 'max_depth = 1' prints the root and its immediate children)
    - print_datatypes <bool> (optional): Print the datatype of the leaf nodes in the tree (i.e., nodes at 'max_depth' are considered leaf nodes) and the datatype of the dictionary keys
    - print_objects <bool> (optional): Print the string representation of the values for the leaf node
    """

    # Make sure the inputs are valid

    is_dict = lambda variable: isinstance(variable, dict) or isinstance(variable, OmegaConf) or isinstance(variable, DictConfig)

    assert is_dict(dictionary), "Argument passed MUST be a dictionary"

    if max_depth:
        assert max_depth >= 0, "Argument must be greater or equal to zero"

    # If 'max_depth = 0', return the name of the root node, if no name is given it doesn't print anything

    if isinstance(max_depth, int) and max_depth == 0:
        if node_name:
            if print_datatypes:
                print("%s%s:%s %s<dict>%s" % (Fore.GREEN, node_name, Fore.WHITE, Fore.RED, Fore.WHITE))
            else:
                print("%s%s%s" % (Fore.GREEN, node_name, Fore.WHITE))
        else:
            return 

    # Initialize output

    global TEMP

    if TEMP == None:
        TEMP = Fore.WHITE

    # Print the name of the root node

    if depth == 0:
        if node_name:
            TEMP += Fore.GREEN + node_name + Fore.WHITE + "\n"

    # Return if maximum depth is reached

    if depth == max_depth:
        return 

    # Print children and recurse if necessary

    num_keys = len(dictionary)
    kdx = 0

    for key, value in dictionary.items():
        TEMP += fill

        if kdx == num_keys - 1:
            TEMP += CLOSING
        else:
            TEMP += BRANCH

        if is_dict(value):
            if max_depth == None or depth < max_depth - 1:
                TEMP += "%s%s%s\n" % (Fore.GREEN, str(key), Fore.WHITE)
                dtree(value, node_name, max_depth, print_datatypes = print_datatypes, print_objects = print_objects, fill = fill + SEPARATOR if kdx < num_keys - 1 else fill + SPACING, depth = depth + 1)
            else:
                if print_datatypes:
                    TEMP += "%s%s:%s %s<dict>%s\n" % (Fore.GREEN, str(key), Fore.WHITE, Fore.RED, Fore.WHITE)
                else:
                    TEMP += "%s%s%s\n" % (Fore.GREEN, str(key), Fore.WHITE)

        else:
            if print_datatypes or print_objects:
                entry = "%s%s:%s " % (Fore.BLUE, str(key), Fore.WHITE)
                if print_datatypes:
                    entry += "%s<%s>%s " % (Fore.RED, type(value).__name__, Fore.WHITE)
                if print_objects:
                    if isinstance(value, list):
                        if len(value) == 0:
                            entry += "%s%s%s" % (Fore.YELLOW, "[]", Fore.WHITE)
                        else:
                            entry += "\n"
                        for idx, item in enumerate(value):
                            if kdx == num_keys - 1:
                                entry += fill + SPACING + "- %s%s%s" % (Fore.YELLOW, str(item), Fore.WHITE)
                            else:
                                entry += fill + SEPARATOR + "- %s%s%s" % (Fore.YELLOW, str(item), Fore.WHITE)
                            if idx < len(value) - 1:
                                entry += "\n"
                    else:
                        entry += "%s%s%s " % (Fore.YELLOW, str(value), Fore.WHITE)
                TEMP += "%s%s\n" % (entry, Fore.WHITE)
            else:
                TEMP += "%s%s%s\n" % (Fore.BLUE, str(key), Fore.WHITE)

        kdx += 1

    if depth == 0:
        output = str(TEMP[:-1])
        TEMP = None
        print(output)
    else:
        return

# %% Testing

if __name__ == "__main__":
    # Example 1
    dictionary = { "A": { "B": { "C": 0, "D": "str" }, "E": None }, "F": { "G": 0.0, "H": set([]) } }
    dtree(dictionary, "with_name")

    #Example 2
    dictionary = { "A": { "B": [0, 1], "C": ["str_1", "str_2", "str_3"] }, "D": None }
    dtree(dictionary, "lists_and_objects", print_objects = True)

# %% End of script
