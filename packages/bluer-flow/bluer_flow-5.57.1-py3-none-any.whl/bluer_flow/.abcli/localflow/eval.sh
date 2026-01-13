#! /usr/bin/env bash

function bluer_flow_localflow_eval() {
    local options=$1
    local type=$(bluer_ai_option "$options" type cpu)
    local verbose=$(bluer_ai_option_int "$options" verbose 0)

    local command_line="${@:2}"

    python3 -m bluer_flow.workflow.runners.localflow \
        eval \
        --command_line "$command_line" \
        --type $type \
        --verbose $verbose
}
