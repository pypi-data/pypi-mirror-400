import os

from bluer_options.help.functions import get_help

from bluer_objects import NAME, VERSION, REPO_NAME, ICON
from bluer_objects import file
from bluer_objects.README.docs import docs
from bluer_objects.README.functions import build
from bluer_objects.README.items import Items
from bluer_objects.help.functions import help_functions


def build_me() -> bool:
    return all(
        build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            macros=readme.get("macros", {}),
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in docs
    )
