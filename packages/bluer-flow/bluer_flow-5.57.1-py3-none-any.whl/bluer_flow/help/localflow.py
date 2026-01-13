from typing import List

from bluer_options.terminal import show_usage, xtra


def help_eval(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("type=<cpu|gpu>,verbose", mono=mono)

    return show_usage(
        [
            "localflow",
            "eval",
            f"[{options}]",
            "<command-line>",
        ],
        "<command-line> -> localflow",
        mono=mono,
    )


def help_list(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("status=<status>", mono=mono)

    return show_usage(
        [
            "localflow",
            "list",
            f"[{options}]",
        ],
        "list localflow jobs.",
        mono=mono,
    )


def help_rm(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("status=<status>", mono=mono)

    return show_usage(
        [
            "localflow",
            "rm",
            f"[{options}]",
        ],
        "rm localflow jobs.",
        mono=mono,
    )


def help_start(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("exit_if_no_job", mono=mono)

    return show_usage(
        [
            "localflow",
            "start",
            f"[{options}]",
        ],
        "start localflow",
        mono=mono,
    )


def help_stop(
    tokens: List[str],
    mono: bool,
) -> str:
    return show_usage(
        [
            "localflow",
            "stop",
        ],
        "stop localflow",
        mono=mono,
    )


help_functions = {
    "eval": help_eval,
    "list": help_list,
    "rm": help_rm,
    "start": help_start,
    "stop": help_stop,
}
