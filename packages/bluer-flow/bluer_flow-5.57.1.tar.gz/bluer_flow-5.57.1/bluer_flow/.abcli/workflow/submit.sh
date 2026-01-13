#! /usr/bin/env bash

function bluer_flow_workflow_submit() {
    local options=$1
    local do_download=$(bluer_ai_option_int "$options" download 1)
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_upload=$(bluer_ai_option_int "$options" upload 1)
    local runner_type=$(bluer_ai_option "$options" to generic)

    local job_name=$(bluer_ai_clarify_object $2 .)

    [[ "$do_download" == 1 ]] &&
        bluer_objects_download - $job_name

    local runner_module="bluer_flow.workflow.runners"
    if [[ "|$BLUER_FLOW_RUNNERS_LIST|" != *"|$runner_type|"* ]]; then
        bluer_ai_log "external runner: $runner_type"

        local var_name=${runner_type}_runner_module_name
        local runner_module=${!var_name}

        if [[ -z "$runner_module" ]]; then
            bluer_ai_log_error "$runner_type: module not found, try exporting $var_name first."
            return 1
        fi
    fi

    bluer_ai_log "📜 workflow.submit: $job_name -$runner_module-> $runner_type"

    python3 -m $runner_module \
        submit \
        --dryrun $do_dryrun \
        --job_name $job_name \
        --runner_type $runner_type
    local status="$?"

    [[ "$do_upload" == 1 ]] &&
        bluer_objects_upload - $job_name

    [[ "$status" -ne 0 ]] && return $status

    if [[ "$runner_type" == local ]]; then
        bluer_ai_cat $ABCLI_OBJECT_ROOT/$job_name/$job_name.sh

        bluer_ai_eval dryrun=$do_dryrun \
            source $ABCLI_OBJECT_ROOT/$job_name/$job_name.sh
        status="$?"
    fi

    return $status
}
