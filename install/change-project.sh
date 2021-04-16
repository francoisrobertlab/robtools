#!/bin/bash

FOLDER_NAME=${PWD##*/}
if [ ! "$FOLDER_NAME" == 'robtools' ] ; then
    echo "You must run change-project.sh from robtools base folder which is expected to be called 'robtools'"
    exit 1
fi

PROJECT=$1
if [ -z "$PROJECT" ] ; then
    echo "You must supply the project name as the first argument"
    exit 1
fi
if [ ! -d "$HOME/projects/$PROJECT" ] ; then
    echo "Project $PROJECT not present in your projects folder"
    exit 1
fi

find install -maxdepth 1 -type f -exec sed -i "s/def-robertf/$PROJECT/g" {} \;
find bash -maxdepth 1 -type f -exec sed -i "s/def-robertf/$PROJECT/g" {} \;
