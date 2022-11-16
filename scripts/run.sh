#!/bin/bash
set -e 

# extract trends
pipenv run main --prepare
pipenv run main --communities
pipenv run main --trends
rm -f trends.log && mv main.log trends.log

# plots
pipenv run plot-network 0 0
pipenv run plot-network 10 0
pipenv run main --plot_timeline
pipenv run plot-alluvial 13
mv main.log alluvial.log