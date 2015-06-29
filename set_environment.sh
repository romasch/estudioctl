#!/bin/bash

# NOTE: source this file at the end 
# of the local .bashrc configuration, 
# with the base directory as argument. Example:

#source ~/work/scripts/set_environment.sh ~/work

# Keep the original PATH variable.
export ORIGINAL_PATH=$PATH
EIFFEL_BASE_PATH=$1

function setenv() {

    if [ $# = 0 ];  then
            echo "Usage: setenv [nightly | stable | local]"
            return
    fi
    
        # General variables
    export EIFFEL_SRC=$EIFFEL_BASE_PATH/source
    export ISE_PLATFORM=linux-x86-64
    
        # ISE_EIFFEL and ISE_LIBRARY
    if [ $1 = 'nightly' ] ; then
            # Source the python-generated correct value for ISE_EIFFEL.
        source $EIFFEL_BASE_PATH/scripts/nightly.unix.sh
        export ISE_LIBRARY=$EIFFEL_SRC
    elif [ $1 = 'stable' ] ; then
        echo "Error: Not implemented!"
        return
    elif [ $1 = 'local' ] ; then
        echo "Error: Not implemented!"
        return
    else
        echo "Error: Unknown option!"
        return
    fi
    
        # Eweasel variables
    export EWEASEL=$EIFFEL_BASE_PATH/eweasel
    export EWEASEL_OUTPUT=$EIFFEL_BASE_PATH/build/eweasel
    export ISE_PRECOMP=$ISE_EIFFEL/precomp/spec/$ISE_PLATFORM

        # PATH variable
    export PATH=$ISE_EIFFEL/studio/spec/$ISE_PLATFORM/bin:$EWEASEL/spec/$ISE_PLATFORM/bin:$EWEASEL/spec/$ISE_PLATFORM/bin:$ORIGINAL_PATH

        # Print variables to allow manual checking.
    echo "ISE_EIFFEL: $ISE_EIFFEL"
    echo "ISE_LIBRARY: $ISE_LIBRARY"
    echo "ISE_PLATFORM: $ISE_PLATFORM"
    echo "ISE_PRECOMP: $ISE_PRECOMP"
    echo "EIFFEL_SRC: $EIFFEL_SRC"
    echo "EWEASEL: $EWEASEL"
    echo "EWEASEL_OUTPUT: $EWEASEL_OUTPUT"
    echo "PATH $PATH"     
}

export -f setenv

