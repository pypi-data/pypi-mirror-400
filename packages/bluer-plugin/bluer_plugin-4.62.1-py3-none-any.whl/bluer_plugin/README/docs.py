from bluer_objects.README.alias import list_of_aliases

from bluer_plugin import NAME
from bluer_plugin.README import aliases, feature_1, feature_2, feature_3
from bluer_plugin.README.items import items

docs = (
    [
        {
            "path": "../..",
            "items": items,
            "macros": {
                "aliases:::": list_of_aliases(NAME),
            },
        },
        {
            "path": "../docs",
        },
    ]
    + aliases.docs
    + feature_1.docs
    + feature_2.docs
    + feature_3.docs
)
