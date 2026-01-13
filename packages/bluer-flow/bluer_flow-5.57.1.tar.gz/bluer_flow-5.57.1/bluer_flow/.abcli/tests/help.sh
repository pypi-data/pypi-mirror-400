#! /usr/bin/env bash

function test_bluer_flow_help() {
    local options=$1

    local module
    for module in \
        "localflow" \
        "localflow eval" \
        "localflow list" \
        "localflow start" \
        "localflow stop" \
        \
        "@flow workflow" \
        "@flow workflow create" \
        "@flow workflow monitor" \
        "@flow workflow submit" \
        \
        "@flow pytest" \
        \
        "@flow test" \
        "@flow test list" \
        \
        "@flow"; do
        bluer_ai_eval ,$options \
            bluer_ai_help $module
        [[ $? -ne 0 ]] && return 1
    done

    return 0
}
