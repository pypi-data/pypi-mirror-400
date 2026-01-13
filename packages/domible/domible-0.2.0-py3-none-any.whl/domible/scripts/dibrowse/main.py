#!/usr/bin/env python
""" domible/scripts/dibrowse/main.py 

script to parse the domible package for all python modules, classes, and functions.
collect source code for each of those objects.
use domible to generate html page of its own source code.
"""

import inspect
from pathlib import Path

import domible 
from domible import open_html_document_in_browser
from domible.starterDocuments import basic_head_empty_body
from domible.elements import Html, Heading, Paragraph
from domible.builders import (
    default_expand_details_button,
    default_collapse_details_button,
    python_code_style,
)

##
# to get dicli in the source code output, need to import its main module.
# dibrowse main module is already imported due to this running script.
import domible.scripts.dicli.main

from .parsedmod import ParsedMod 

import argparse
import importlib

def module_type(module_name):
    """
    Custom type function to import a module by name.
    defined here to use in parser.add_argument.
    """
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        raise argparse.ArgumentTypeError(f"Cannot import module '{module_name}': {e}")

dibrowse_help = """ show source code for given python module.
defaults to domible package,
but, in theory, should work with any non builtin module.
Only shows native python code though.
"""
module_help = """ name of module to parse and display its python code """
parser = argparse.ArgumentParser(
    prog="dibrowse",
    description=dibrowse_help,
    formatter_class=argparse.RawTextHelpFormatter,
    epilog="Cheers!",
)

parser.add_argument("module", nargs="?", default="domible", type=module_type, help=module_help)
args = parser.parse_args()


def run():
    modname = args.module.__name__
    print(f"parsing module {modname}")
    module_html_focused = ParsedMod(args.module).parse().get_html()
    title: str = f"Source Code for the {modname} package"
    html_doc = basic_head_empty_body(title)
    html_doc.add_elements_to_head(python_code_style)
    html_doc.add_contents_to_body([
        default_expand_details_button(), 
        default_collapse_details_button(),
        Heading(1, title),
        Paragraph(f"Root path for {modname}: {Path(inspect.getfile(args.module)).parent}"),
        module_html_focused,
    ])
    open_html_document_in_browser(html_doc)

if __name__ == "__main__":
    run()

## end of file
