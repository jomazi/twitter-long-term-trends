# Twitter Long-term Trends

## Setup

1. Make sure to have `python version 3.9` installed: `python --version`
2. Check if [Pipenv](https://pipenv.pypa.io/en/latest/) is installed: `pipenv --version`
3. Install the [Cairo](https://cairographics.org/) graphics library: see the [Pycairo docs](https://pycairo.readthedocs.io/en/latest/getting_started.html) for more details
4. Install dependencies (including development requirements): `pipenv install --dev`

## Analysis tasks

Before starting with the analysis tasks please make sure that in `src/utils/config.py` the configuration is set according to your needs. If you make any changes (e.g., adjusting the number of snapshots), please also change the script `scripts/init-trends-dir.sh` accordingly. After that the following analysis tasks can be executed (please take the chronological order into account):

1. Prepare data: `pipenv run main --prepare`
2. Detect temporal communities: `pipenv run main --communities`
3. Extract trends: `pipenv run main --trends`
4. Plot trend network: e.g., `pipenv run plot-network 0 0` (snapshot id: 0, trend id: 0) or `pipenv run plot-network 10 0` (snapshot id: 10, trend id: 0)
5. Plot temporal heatmap of trends: `pipenv run main --plot_timeline`
6. Plot alluvial diagram: `pipenv run plot-alluvial 13` (snapshot id: 13)

## Data requirements

1. Hashtag occurrence data should be stored in the `data/nodes` folder. For each snapshot one `.csv` file should be provided. It should be named by following this convention: `<unix time stamp start>-<unix time stamp stop>.csv`. Sample data (e.g., stored in the file `1609459200-1612137600.csv`) might look like this (including the csv header):

    ```csv
    node,count
    corona,10
    covid,250
    ```

2. Following the same naming convention as the node-related data, hashtag co-occurrence information is stored in the `data/edges` folder. Edges are assumed to be given in both directions. Sample data might look like this:

    ```csv
    source,target,timestamp
    covid,corona,1611058321
    corona,covid19,1611058321
    ```

3. Inside the `data` folder provide a file named `tweets.csv`. It should contain the number of total tweets per snapshot and be structured as indicated by the sample data:

    ```csv
    start,stop,count
    1609459200,1612137600,120592    
    ```
