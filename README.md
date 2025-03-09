# Dashboard Analisis Kualitas Udara ✨

## Setup Environment - Anaconda
```
conda create --name AQI-ds python=3.11.7
conda activate AQI-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal
```
mkdir air_quality_analysis
cd air_quality_analysis
conda install -c plotly plotly
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run steamlit app
```
streamlit run dashboard.py
```
