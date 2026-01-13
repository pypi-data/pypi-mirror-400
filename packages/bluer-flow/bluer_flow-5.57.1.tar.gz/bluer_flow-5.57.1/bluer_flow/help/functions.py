from bluer_ai.help.generic import help_functions as generic_help_functions

from bluer_flow import ALIAS
from bluer_flow.help.localflow import help_functions as help_localflow
from bluer_flow.help.workflow import help_functions as help_workflow

help_functions = generic_help_functions(plugin_name=ALIAS)


help_functions.update(
    {
        "localflow": help_localflow,
        "workflow": help_workflow,
    }
)
