#! /usr/bin/env bash

function test_bluer_flow_localflow_stop() {
    local options=$1

    bluer_ai_eval dryrun=$do_dryrun \
        bluer_flow_localflow_stop
}
