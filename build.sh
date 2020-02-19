#!/usr/bin/env sh

echo "Setting BUILD"
find . -name .git -type d -prune -o -type f -name constants.py -exec sed -i "s/^BUILD.*/BUILD\ =\ \'${CI_PIPELINE_ID:-None}\'/g" {} + -exec grep BUILD {} +
