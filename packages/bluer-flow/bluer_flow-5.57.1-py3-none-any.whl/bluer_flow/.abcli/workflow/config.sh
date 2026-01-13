#! /usr/bin/env bash

export BLUER_FLOW_RUNNERS_LIST=$(python3 -m bluer_flow.workflow.runners list --delim \|)

export BLUER_FLOW_PATTERNS_LIST=$(python3 -m bluer_flow.workflow.patterns list --delim \|)

export BLUER_FLOW_PATTERN_DEFAULT=$(python3 -m bluer_flow.workflow.patterns list --count 1)
