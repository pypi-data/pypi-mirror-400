from functools import reduce

from bluer_options import string

from bluer_flow.workflow.patterns import list_of_patterns
from bluer_flow.workflow.runners import list_of_runners


items = (
    ["📜"]
    + [
        "[`{}`](./patterns/{}.dot)".format(
            pattern,
            pattern,
        )
        for pattern in list_of_patterns()
    ]
    + reduce(
        lambda x, y: x + y,
        [
            (
                [
                    (
                        f"[{runner_type}](./bluer_flow/workflow/runners/{runner_type}/runner.py)"
                        if runner_type == "localflow"
                        else f"[{runner_type}](./bluer_flow/workflow/runners/{runner_type}.py)"
                    )
                ]
                + [
                    f"[![image]({url})]({url}) [🔗]({url})"
                    for url in [
                        "https://github.com/kamangir/assets/blob/main/bluer_flow-{}-{}/workflow.gif?raw=true&random={}".format(
                            runner_type,
                            pattern,
                            string.random(),
                        )
                        for pattern in list_of_patterns()
                    ]
                ]
            )
            for runner_type in list_of_runners()
        ],
        [],
    )
)
