#! /usr/bin/env bash

function test_bluer_flow_localflow_eval() {
    local options=$1

    bluer_flow_localflow \
        eval \
        ,$options \
        bluer_ai version
}
