#! /usr/bin/env bash

function test_bluer_flow_workflow_runner() {
    local options=$1
    local do_dryrun=$(bluer_ai_option_int "$options" dryrun 0)
    local do_publish=1
    [[ "$abcli_is_github_workflow" == true ]] &&
        do_publish=0
    local do_publish=$(bluer_ai_option_int "$options" publish $do_publish)
    local list_of_runners=$(bluer_ai_option "$options" runner $BLUER_FLOW_RUNNERS_LIST)
    local list_of_patterns=$BLUER_FLOW_PATTERNS_LIST
    [[ "$abcli_is_github_workflow" == true ]] &&
        list_of_patterns="a-bc-d"
    list_of_patterns=$(bluer_ai_option "$options" pattern $list_of_patterns)

    local pattern
    local runner
    for runner in $(echo $list_of_runners | tr \| " "); do
        for pattern in $(echo $list_of_patterns | tr \| " "); do
            bluer_ai_log "📜 testing runner=$runner, pattern=$pattern ..."

            local job_name=test-$runner-$pattern-$(bluer_ai_string_timestamp)

            bluer_flow_workflow_create \
                pattern=$pattern \
                $job_name \
                --publish_as $runner-$pattern
            [[ $? -ne 0 ]] && return 1

            bluer_flow_workflow_submit \
                to=$runner \
                $job_name
            [[ $? -ne 0 ]] && return 1

            if [[ "$runner" == "localflow" ]]; then
                bluer_flow_localflow_start \
                    exit_if_no_job
                [[ $? -ne 0 ]] && return 1
            fi

            bluer_flow_workflow_monitor \
                publish_as=$runner-$pattern \
                $job_name
            [[ $? -ne 0 ]] && return 1

            if [[ "$do_publish" == 1 ]]; then
                bluer_sandbox_assets_publish \
                    extensions=gif,push \
                    $job_name \
                    --asset_name bluer_flow-$runner-$pattern
            fi

            bluer_ai_hr
        done
    done
}
