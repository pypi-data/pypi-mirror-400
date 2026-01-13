from blueness.pypi import setup

from bluer_flow import NAME, VERSION, DESCRIPTION, REPO_NAME


setup(
    filename=__file__,
    repo_name=REPO_NAME,
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    packages=[
        NAME,
        f"{NAME}.help",
        f"{NAME}.workflow",
        f"{NAME}.workflow.patterns",
        f"{NAME}.workflow.runners",
    ],
    include_package_data=True,
    package_data={
        NAME: [
            "config.env",
            "sample.env",
            ".abcli/**/*.sh",
            "**/*.dot",
        ],
    },
)
