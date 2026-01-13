#! /usr/bin/env bash

function bluer_flow_workflow_create() {
    local options=$1
    local do_upload=$(bluer_ai_option_int "$options" upload 1)
    local pattern=$(bluer_ai_option "$options" pattern $BLUER_FLOW_PATTERN_DEFAULT)

    local job_name=$(bluer_ai_clarify_object $2 .)

    bluer_ai_log "📜 workflow.create: $pattern -> $job_name"

    python3 -m bluer_flow.workflow \
        create \
        --job_name $job_name \
        --pattern "$pattern" \
        "${@:3}"
    local status=$?

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload - $job_name

    return $status
}
