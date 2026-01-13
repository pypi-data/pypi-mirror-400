from bluer_options.env import load_config, load_env, get_env

load_env(__name__)
load_config(__name__)


BLUER_FLOW_DEFAULT_WORKFLOW_PATTERN = get_env("BLUER_FLOW_DEFAULT_WORKFLOW_PATTERN")

LOCALFLOW_SLEEP_BETWEEN_JOBS = get_env("LOCALFLOW_SLEEP_BETWEEN_JOBS", 3)
