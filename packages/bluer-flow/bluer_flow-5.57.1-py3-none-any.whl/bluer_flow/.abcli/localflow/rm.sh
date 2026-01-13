#! /usr/bin/env bash

function bluer_flow_localflow_rm() {
    local options=$1
    local list_of_status=$(bluer_ai_option "$options" status PENDING+RUNNABLE+RUNNING+FAILED)

    local status
    for status in $(echo $list_of_status | tr + " "); do
        bluer_ai_log "$status"

        local job_name
        for job_name in $(bluer_objects_mlflow_tags_search \
            contains=localflow-job,status=$status \
            --delim space \
            --log 0); do
            bluer_objects_mlflow_tags_set \
                $job_name \
                status=DELETED
        done
    done

    return 0
}
