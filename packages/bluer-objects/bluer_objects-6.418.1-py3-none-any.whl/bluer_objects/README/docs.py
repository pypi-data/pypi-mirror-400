from bluer_objects import NAME
from bluer_objects.README import aliases, modules
from bluer_objects.README.alias import list_of_aliases

docs = (
    [
        {
            "path": ".",
        },
        {
            "path": "../..",
            "macros": {
                "aliases:::": list_of_aliases(NAME),
            },
        },
        {
            "path": "../docs",
        },
    ]
    + aliases.docs
    + modules.docs
)
