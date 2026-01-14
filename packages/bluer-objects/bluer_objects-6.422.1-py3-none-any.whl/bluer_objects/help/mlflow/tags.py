from typing import List

from bluer_options.terminal import show_usage

from bluer_objects import env

search_args = [
    "[--count <-1>]",
    "[--delim <space>]",
    "[--log <0>]",
    "[--offset <0>]",
]


def help_clone(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "@tags",
            "clone",
            "[..|<object-1>]",
            "[.|<object-2>]",
        ],
        "clone mlflow tags.",
        mono=mono,
    )


def help_get(
    tokens: List[str],
    mono: bool,
) -> str:
    args = ["[--tag <tag>]"]

    return show_usage(
        [
            "@tags",
            "get",
            "[.|<object-name>]",
        ]
        + args,
        "get mlflow tags|<tag> for <object-name>.",
        mono=mono,
    )


def help_search(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "<keyword-1>=<value-1>,<keyword-2>,~<keyword-3>"

    usage_1 = show_usage(
        [
            "@tags",
            "search",
            f"[{options}]",
        ]
        + search_args,
        "search mlflow.",
        mono=mono,
    )

    if env.MLFLOW_IS_SERVERLESS:
        return usage_1

    # ---

    args = sorted(
        [
            "[--server_style 1]",
            "[--filter_string <filter-string>]",
        ]
        + search_args
    )

    usage_2 = show_usage(
        [
            "@tags",
            "search",
        ]
        + args,
        "search mlflow server for <filter-string>.",
        {
            "<filter-string>: https://www.mlflow.org/docs/latest/search-experiments.html": ""
        },
        mono=mono,
    )

    # ---

    return "\n".join(
        [
            usage_1,
            usage_2,
        ]
    )


def help_set(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "<keyword-1>=<value>,<keyword-2>,~<keyword-3>"

    args = [
        "[--verbose 1]",
    ]

    return show_usage(
        [
            "@tags",
            "set",
            "[.|<object-name>]",
            f"[{options}]",
        ]
        + args,
        "set tags in mlflow.",
        mono=mono,
    )


help_functions = {
    "clone": help_clone,
    "get": help_get,
    "search": help_search,
    "set": help_set,
}
