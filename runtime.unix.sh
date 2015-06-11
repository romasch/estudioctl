#!/bin/bash

cd $EIFFEL_SRC/C

if [ -f config.sh ]; then
	rm config.sh
fi
cp CONFIGS/$ISE_PLATFORM config.sh

# if [ $allmakefiles != no ]; then
# 	./Configure -S
# fi 

source ./eif_config_h.SH
cd run-time
source ./eif_size_h.SH
cd ..
cp eif_*.h run-time/

