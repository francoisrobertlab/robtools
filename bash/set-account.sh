VENV="$HOME/robtools-venv"
BASH="$VENV"/bash
ACCOUNT=$1

if [[ ! "$ACCOUNT" =~ ^def-[a-zA-Z0-9]+$ ]]
then
    echo "You must supply your account id (ex: def-robertf) as the first argument"
    exit 1
fi

find "$BASH" -type f -name "*.sh" -exec sed -i "s/--account\=[a-zA-Z0-9-]*/--account\=$ACCOUNT/g" {} \;
