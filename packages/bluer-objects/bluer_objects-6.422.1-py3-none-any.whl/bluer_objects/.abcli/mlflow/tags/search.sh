#! /usr/bin/env bash

function bluer_objects_mlflow_tags_search() {
    python3 -m bluer_objects.mlflow \
        search \
        --tags "$1" \
        "${@:2}"
}
