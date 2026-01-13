#! /usr/bin/env bash

function bluer_flow_workflow_monitor() {
    local options=$1
    local do_download=$(bluer_ai_option_int "$options" download 1)
    local do_upload=$(bluer_ai_option_int "$options" upload 1)
    local node=$(bluer_ai_option "$options" node void)

    local job_name=$(bluer_ai_clarify_object $2 .)

    bluer_ai_log "📜 workflow.monitor: $job_name @ $node ..."

    [[ "$do_download" == 1 ]] &&
        bluer_objects_download - $job_name

    python3 -m bluer_flow.workflow.runners \
        monitor \
        --hot_node $node \
        --job_name $job_name

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload - $job_name

    local command_line="${@:3}"
    [[ -z "$command_line" ]] && return 0

    bluer_ai_eval - \
        "$command_line"
}
