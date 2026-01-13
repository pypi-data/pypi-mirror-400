"""domible/scripts/dibrowse/parsedmod.py

ParsedMod works similarly to element_from_object in the builders.
For a given module,
get all the modules, functions, and classes directly in the modules namespace.
For each module in the namespace, recurse into it and do the same thing.

For the HTML,
Build up a tree of details elements with the object name as the summary.
The contents will be the module's source code and list of any modules contained by that module.
Termination of a branch is when a module has only classes and functions.

First list the modules that are sub packages
next list modules that are files within a directory.
Last list all non module members in the module, e.g., functions, classes, others.
Nothing should be listed in more than one place.
"""

import inspect
from pathlib import Path
from typing import Self

import domible
from domible.elements import Details, Summary, UnorderedList, ListItem
from domible.builders import python_code_block

def is_package(module) -> bool:
    """
    inspect.ispackage was added in python 3.14.
    rolling my own limited version for now.
    """
    return hasattr(module, '__path__')


def is_builtin(member) -> bool:
    """ 
    inspect.isbuiltin() does not check for buildin modules (e.g., sys).
    rolling my own.
    """
    if not inspect.ismodule(member):
        if inspect.isbuiltin(member): return True
    else:  #  check if it is a builtin module.
        try:
            inspect.getfile(member)
            return False
        except TypeError:
            return True


def get_name(obj):
    """Get the most descriptive name for any object."""
    # Try __name__ first (functions, classes, modules)
    if hasattr(obj, "__name__"):
        return obj.__name__

    # Try __class__.__name__ (instances)
    if hasattr(obj, "__class__"):
        return obj.__class__.__name__
    # Fallback to type name
    return type(obj).__name__


"""
get_leaf_html and get_module_html are the brute force, 
show all members returned by inspect.getmembers()
and display them in a details element.
There is some filtering to ensure we don't dig into modules not defined within domible.
There is a bit of creep though with non module imports (e.g., Any).
"""

def get_leaf_html(leaf: object, name: str = None) -> Details | str:
    """
    Leaf isn't really the right name, I'm abusing the tree metaphore.
    Leaf in this case simply means the object is not a module, thus do not recurse into it.
    A 'leaf' is a class, function, or other, and we simply want a Details element with its name and source code.
    There is no branch continuing from this object.

    passing in the "name" from inspect.getmembers.
    It might be different from what's found in get_name,
    specifically for instances of classes exposed at module level 
    (imported in __init__.py).
    """
    leaf_name = get_name(leaf)
    if inspect.isclass(leaf): leaf_type = "class"
    elif inspect.isfunction(leaf): leaf_type = "function"
    else: leaf_type = "other"
    try:
        source_code = python_code_block(inspect.getsource(leaf))
        return Details(Summary(f"{leaf_type}: {leaf_name}"),source_code)
    except Exception as ex:
        return f"{name} ({leaf_name}) - cannot find source, object is likely an instance variable"


class ParsedMod:
    """
    ParsedMod has a reference to the mod itself, some meta data, then
    - lists of sub modules (indicating the parsed module is likely a package),
    - non module objects defined within the module (e.g., classes and functions).
    - list of likely instance variables.
    Only .py files should have classes and functions and other non module definitions.
    All the conditionals comparing paths and files and attributes,
    are attempts to determine if the member being considered is actually defined in the module being parsed.
    This in large part is due to imported items show up in the inspect.getmembers(module) output.
    I could do this using asattr, looking for __path__ and __module__ attributes.
    I already did it using paths though which seems to work as well.
    """

    def __init__(self, module):
        if not inspect.ismodule(module):
            raise ValueError(
                f"argument, {get_name(module)}, to ParsedModule must be a module"
            )
        self.module = module
        self.mod_name = get_name(module)
        self.mod_file = Path(inspect.getfile(module))
        self.mod_path = Path(inspect.getfile(module)).parent
        self.sub_mods = []
        self.not_mods = []  # e.g., classes and functions
        self.instances = []  # objects that except on inspect.getfile()

    def parse(self) -> Self:
        ## print(f"parsing {self.mod_name}")
        for name, member in inspect.getmembers(self.module):
            if is_builtin(member) or name.startswith("_"):
                # ignore dunder and private methods and variables
                continue

            if inspect.ismodule(member):
                print(f"module {get_name(member)}")
                # if we're looking at a module, check that it is defined directly within the module being parsed.
                # if so, recursively parse the module and add it to the list of sub modules.
                # otherwise, it can be ignored.
                # inspect.getfile() ends with the __init__.py file for packages,
                # and the source file for code modules, thus the .parent.
                m_path = Path(inspect.getfile(member)).parent
                if (
                    m_path
                    == self.mod_path  # member is likely a py file within the package
                    or m_path.parent == self.mod_path
                ):  # mod is a sub package
                    self.sub_mods.append(ParsedMod(member).parse())
            else:  # it's a function, class, or something else.
                # check that it is defined within this module and save it for later if so.
                # getfile() will error if, for example, member is an instance variable.
                # save a string for each instance variable.
                try:
                    nm_file = Path(inspect.getfile(member))
                    if nm_file == self.mod_file:
                        ## print(f"saving {get_name(member)}")
                        self.not_mods.append(member)
                except:
                    self.instances.append(
                        f"{name}: {get_name(member)} - probably an instance variable"
                    )
        return self

    def get_html(self) -> Details:
        """
        create a Details element with the module name as summary,
        then list of module source code, other modules, non module defs and instance objects.
        """
        mod_src = Details(
            Summary("Source Code"), python_code_block(inspect.getsource(self.module))
        )
        ul = UnorderedList()
        ul.add_content([ListItem(mod_src)])
        modtype = "package" if is_package(self.module) else "code file"
        details_mod = Details(Summary(f"{modtype}: {self.mod_name}"), ul)
        # We hve the Details element for the module,
        # now add any sub modules and other definitions to the list (ul).
        if len(self.sub_mods) > 0:
            ul.add_content([ListItem(m.get_html()) for m in self.sub_mods])
        # now look at objects that are not mods, but also do not error on inspect.getfile()
        # These are most likely class and function definitions.
        if len(self.not_mods) > 0:
            ul.add_content([ListItem(get_leaf_html(nm)) for nm in self.not_mods])
        # and finally get the strings of objects that error on inspect.getfile(), instance variables.
        if len(self.instances) > 0:
            ul.add_content([ListItem(inst) for inst in self.instances])
        return details_mod


# end of file
