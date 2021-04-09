#!/bin/bash

PROJECT=$1
if [ -z "$PROJECT" ] ; then
    echo "You must supply the project name as the first argument"
    exit 1
fi
if [ ! -d "$HOME/projects/$PROJECT" ] ; then
    echo "Project $PROJECT not present in your projects folder"
    exit 1
fi

find . -maxdepth 1 -type f -exec sed -i "s/def-robertf/$PROJECT/g" {} \;
