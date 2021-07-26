import streamlit as st

import numpy as np
import pandas as pd
import time

st.header("My F1 Python Web App")

readme = st.checkbox("readme first!")

if readme:

    st.write("""
        This is a web app demo using [streamlit](https://streamlit.io/) library. It is hosted in [Streamlit Sharing](https://share.streamlit.io/). You may get the codes via [github](https://github.com/blueapple16/F1)
        """)
    st.write ("For more info, please contact:")

    st.write("<a href='https://www.linkedin.com/in/kah-wee-lim-02836a76/'> Kah Wee </a>", unsafe_allow_html=True)

option = st.sidebar.selectbox(
    'Select an option',
     ['Locations of Grand Prix','map','T n C','Long Process'])

#import database
import matplotlib.pyplot as plt
from IPython.display import HTML, display
import urllib

circuits = read_csv('circuits.csv', index_col=0)
constructorResults = read_csv('constructor_results.csv', index_col=0)
constructors = read_csv('constructors.csv', index_col=0)
constructorStandings = read_csv('constructor_standings.csv', index_col=0)
drivers = read_csv('drivers.csv', index_col=0)
driverStandings = read_csv('driver_standings.csv', index_col=0)
lapTimes = read_csv('lap_times.csv')
pitStops = read_csv('pit_stops.csv')
qualifying = read_csv('qualifying.csv', index_col=0)
races = read_csv('races.csv', index_col=0)
results = read_csv('results.csv', index_col=0)
seasons = read_csv('seasons.csv', index_col=0)
status = read_csv('status.csv', index_col=0)
#end import

if option=='Locations of Grand Prix':
#     chart_data = pd.DataFrame(
#     np.random.randn(20, 3),
#     columns=['a', 'b', 'c'])

#     st.line_chart(chart_data)
map_data = pd.DataFrame(
    columns=['lat', 'lon'])
map_data.lat = circuits['lat']
map_data.lon = circuits['lng']

    st.map(map_data)



#ori below

elif option=='map':
    map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

    st.map(map_data)

elif option=='T n C':

    st.write('Before you continue, please read the [terms and conditions](https://www.gnu.org/licenses/gpl-3.0.en.html)')
    show = st.checkbox('I agree the terms and conditions')
    if show:
        st.write(pd.DataFrame({
        'Intplan': ['yes', 'yes', 'yes', 'no'],
        'Churn Status': [0, 0, 0, 1]
        }))


else:
    'Starting a long computation...'

    
    latest_iteration = st.empty()
    bar = st.progress(0)

    for i in range(100):
   
        latest_iteration.text(f'Iteration {i+1}')
        bar.progress(i + 1)
        time.sleep(0.1)

    '...and now we\'re done!'
