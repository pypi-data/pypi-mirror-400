#! /usr/bin/env bash

function bluer_flow_localflow_stop() {
    local hash=$(bluer_ai_string_random)

    bluer_objects_mlflow_tags_set \
        localflow \
        hash=$hash
}
