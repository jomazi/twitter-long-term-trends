#!/bin/bash
set -e 

cd $PWD/data/trends
dir_names=( "0" "1" "2" "3" "4" "5" "6" "7" "8" "9" "10" "11" "12" "13" "14" "15" "16" "17" "complete" )

# snapshots
for d in "${dir_names[@]}"; do
    mkdir $d
    cd $d
    # trend
    for ((x = 0 ; x <= 9 ; x++)); do 
        mkdir $x
        cd $x
        touch .gitkeep
        cd ..
    done
    cd ..
done