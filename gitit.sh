#!/bin/bash
module load git

message="$*"

if [[ "X$message" == "X" ]]; then
    message="NO MESSAGE"
fi

git add .
git commit -m "$message"
git push origin master
