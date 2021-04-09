#!/bin/bash

if [ "$1" == "clean" ] ; then
    echo "Removing changes made to .bash_profile"
    if ! grep -Fq "source .def-robert-addons" ~/.bash_profile ; then
        INDEX=$(grep -n "source .def-robert-addons" ~/.bash_profile | cut -d: -f1)
        sed -i "$((INDEX-1)),$((INDEX+2))d" ~/.bash_profile
    fi
    if [ -f ~/.def-robert-addons ] ; then
        rm ~/.def-robert-addons
    fi
    exit 0
fi

# Remove direct configuration of robert lab modules, if present.
if grep -Fq "ROBERTF_MODULES_DIR=" ~/.bash_profile ; then
    echo "Removing Robert Lab modules from .bash_profile"
    INDEX=$(grep -n "ROBERTF_MODULES_DIR=" ~/.bash_profile | cut -d: -f1)
    sed -i "$((INDEX-1)),$((INDEX+4))d" ~/.bash_profile
fi

# Source .def-robert-addons file on login.
if ! grep -Fq "source .def-robert-addons" ~/.bash_profile ; then
    echo "Adding Robert Lab addons"
    echo 'if [ -f .def-robert-addons ]; then' >> ~/.bash_profile
    echo '  source .def-robert-addons' >> ~/.bash_profile
    echo 'fi' >> ~/.bash_profile
    echo "" >> ~/.bash_profile
fi

# Create .def-robert-addons file to alow loading of robert modules.
if [ -f ~/.def-robert-addons ] ; then
    rm ~/.def-robert-addons
fi
echo "## Robert Lab Modules ##" >> ~/.def-robert-addons
echo "MODULES_DIR=~/projects/def-robertf/modules" >> ~/.def-robert-addons
echo 'if [ -d "$MODULES_DIR" ]; then' >> ~/.def-robert-addons
echo '  module use $MODULES_DIR' >> ~/.def-robert-addons
echo 'fi' >> ~/.def-robert-addons
echo "" >> ~/.def-robert-addons
