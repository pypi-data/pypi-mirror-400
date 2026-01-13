import os

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_flow import NAME, VERSION, ICON, REPO_NAME
from bluer_flow.workflow.README import items as workflow_items
from bluer_flow.workflow.patterns import list_of_patterns
from bluer_flow.help.functions import help_functions


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            cols=len(list_of_patterns()) + 1,
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in [
            {"items": workflow_items, "path": ".."},
            # aliases
            {"path": "docs/aliases/localflow.md"},
            {"path": "docs/aliases/workflow.md"},
        ]
    )
