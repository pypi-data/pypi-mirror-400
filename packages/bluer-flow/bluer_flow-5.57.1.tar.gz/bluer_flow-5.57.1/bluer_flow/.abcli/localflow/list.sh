#! /usr/bin/env bash

function bluer_flow_localflow_list() {
    local options=$1
    local list_of_status=$(bluer_ai_option "$options" status PENDING+RUNNABLE+RUNNING+FAILED)

    local status
    for status in $(echo $list_of_status | tr + " "); do
        bluer_ai_log "$status"

        bluer_objects_mlflow_tags_search \
            contains=localflow-job,status=$status \
            --item_name_plural "job(s)" \
            --log 1
    done

    return 0
}
