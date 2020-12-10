#!/bin/bash

VENV="$HOME/robtools-venv"
BASH="$VENV"/bash
ROBTOOLS="$VENV"/robtools
ROBTOOLS_BASH="$ROBTOOLS"/bash
EMAIL="$JOB_MAIL"
BRANCH="master"

if [ "$1" == "clean" ]
then
    echo "Removing python virtual environment at $VENV"
    rm -R "$VENV"
    exit 0
fi
if [[ ! "$EMAIL" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$ ]]
then
    echo "Could not find your email address. Did you run configure.sh?"
    exit 1
fi
if [ ! -d "$VENV" ]
then
    echo "Creating python virtual environment at $VENV"
    python3 -m venv "$VENV"
fi
if [ ! -z "$1" ]
then
    BRANCH="$1"
    echo "Selected branch $BRANCH for robtools"
fi
echo "Updating python libraries"
pip uninstall -y RobTools SeqTools
pip install git+https://git@github.com/francoisrobertlab/robtools.git@"$BRANCH"
echo "Updating bash scripts"
rm -R "$BASH"
mkdir "$BASH"
git clone --depth 1 -c advice.detachedHead=false --branch "$BRANCH" https://github.com/francoisrobertlab/robtools.git "$ROBTOOLS"
cp "$ROBTOOLS_BASH"/*.sh "$BASH"
find "$BASH" -type f -name "*.sh" -exec sed -i "s/christian\.poitras@ircm\.qc\.ca/$EMAIL/g" {} \;
rm -Rf "$ROBTOOLS"
if [ -f "$BASH"/install.sh ]
then
    rm "$BASH"/install.sh
fi
