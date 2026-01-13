#! /usr/bin/env bash

function bluer_flow_localflow_start() {
    local options=$1
    local exit_if_no_job=$(bluer_ai_option_int "$options" exit_if_no_job 0)

    [[ "$MLFLOW_DEPLOYMENT" == "local" ]] &&
        bluer_ai_log_warning "export MLFLOW_DEPLOYMENT=https://..."

    local localflow_hash=$(bluer_objects_mlflow_tags_get \
        localflow \
        --tag hash)
    bluer_ai_log "⏳ hash: $localflow_hash"

    while true; do
        local localflow_hash_latest=$(bluer_objects_mlflow_tags_get \
            localflow \
            --tag hash)
        if [[ "$localflow_hash_latest" != "$localflow_hash" ]]; then
            bluer_ai_log "⏳ hash changed: $localflow_hash_latest <> $localflow_hash"
            return 0
        fi

        local job_name=$(python3 -m bluer_flow.workflow.runners.localflow \
            find_job)
        if [[ -z "$job_name" ]]; then
            bluer_ai_log "⏳ no job found."
            [[ "$exit_if_no_job" == "1" ]] &&
                return 0

            bluer_ai_sleep $LOCALFLOW_SLEEP_BETWEEN_JOBS
            continue
        fi

        bluer_objects_download - $job_name

        bluer_ai_log "⏳ found job: $job_name"
        local command_line=$(bluer_objects_metadata_get \
            key=command_line,object \
            $job_name)
        command_line=${command_line//\"/}

        bluer_ai_log "⏳ command: $command_line"
        bluer_ai_eval - $command_line
        local status="$?"

        python3 -m bluer_flow.workflow.runners.localflow \
            complete_job \
            --job_name $job_name \
            --status $status

        bluer_ai_hr
    done

}
