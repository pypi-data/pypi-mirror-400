#! /usr/bin/env bash

function test_bluer_flow_README() {
    local options=$1

    bluer_ai_eval ,$options \
        bluer_flow build_README
}
