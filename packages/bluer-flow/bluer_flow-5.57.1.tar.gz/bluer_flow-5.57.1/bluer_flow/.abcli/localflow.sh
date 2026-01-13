#! /usr/bin/env bash

function bluer_flow_localflow() {
    local task=${1:-start}

    local function_name=bluer_flow_localflow_$task
    if [[ $(type -t $function_name) == "function" ]]; then
        $function_name "${@:2}"
        return
    fi

    python3 -m bluer_flow.workflow.runners.localflow "$@"
}

bluer_ai_source_caller_suffix_path /localflow
