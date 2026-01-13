#! /usr/bin/env bash

function bluer_flow() {
    local task=$1

    bluer_ai_generic_task \
        plugin=bluer_flow,task=$task \
        "${@:2}"
}

bluer_ai_source_caller_suffix_path /tests

bluer_ai_env_dot_load \
    caller,plugin=bluer_flow,suffix=/../..

bluer_ai_env_dot_load \
    caller,filename=config.env,suffix=/..

bluer_ai_log $(bluer_flow version --show_icon 1)
