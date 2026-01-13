from blueness import module
from bluer_options.help.functions import help_main

from bluer_flow import NAME
from bluer_flow.help.functions import help_functions

NAME = module.name(__file__, NAME)


help_main(NAME, help_functions)
