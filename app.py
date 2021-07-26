import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import HTML, display
import urllib

def read_csv(name, **kwargs):
    df = pd.read_csv(f'../input/formula-1-race-data/{name}', na_values=r'\N', **kwargs)
    return df

# create replacement raceId that is ordered by time
def race_key(race_year, race_round):
    # My bet: we won't get to 100 races per year :)
    return (race_year * 100) + race_round

def races_subset(df, race_ids):
    df = df[df.raceId.isin(race_ids)].copy()
    df = df.join(races[['round', 'raceKey']], on='raceId')
    df['round'] -= df['round'].min()
    # drop_duplicates: duplicate entries have appeared in 2021
    # race:1051 driver:832
    return df.set_index('round').sort_index().drop_duplicates()

IMG_ATTRS = 'style="display: inline-block;" width=16 height=16'
YT_IMG = f'<img {IMG_ATTRS} src="https://youtube.com/favicon.ico">'
WK_IMG = f'<img {IMG_ATTRS} src="https://wikipedia.org/favicon.ico">'
GM_IMG = f'<img {IMG_ATTRS} src="https://maps.google.com/favicon.ico">'

# Read data
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

# To sequence the races if they did not happen in order of raceId (ie. 2021)
races['raceKey'] = race_key(races['year'], races['round'])

# For display in HTML tables
drivers['display'] = drivers.surname
drivers['Driver'] = drivers['forename'] + " " + drivers['surname']
drivers['Driver'] = drivers.apply(lambda r: '<a href="{url}">{Driver}</a>'.format(**r), 1)
constructors['label'] = constructors['name']
constructors['name'] = constructors.apply(lambda r: '<a href="{url}">{name}</a>'.format(**r), 1)

# Join fields
results['status'] = results.statusId.map(status.status)
results['Team'] = results.constructorId.map(constructors.name)
results['score'] = results.points>0
results['podium'] = results.position<=3

# Cut data to one year
races = races.query('year==@YEAR').sort_values('round').copy()
results = results[results.raceId.isin(races.index)].copy()
lapTimes = lapTimes[lapTimes.raceId.isin(races.index)].copy()
# Save Ids of races that have actually happened (i.e. have valid lap-times).
race_ids = np.unique(lapTimes.raceId)
driverStandings = races_subset(driverStandings, race_ids)
constructorStandings = races_subset(constructorStandings, race_ids)


lapTimes = lapTimes.merge(results[['raceId', 'driverId', 'positionOrder']], on=['raceId', 'driverId'])
lapTimes['seconds'] = lapTimes.pop('milliseconds') / 1000

# Processing for Drivers & Constructors championship tables
def format_standings(df, key):
    df = df.sort_values('position')
    gb = results.groupby(key)
    df['Position'] = df.positionText
    df['points'] = df.points.astype(int)
    df['scores'] = gb.score.sum().astype(int)
    df['podiums'] = gb.podium.sum().astype(int)
    for c in [ 'scores', 'points', 'podiums', 'wins' ]:
        df.loc[df[c] <= 0, c] = ''
    return df

# Drivers championship table
def drivers_standings(df):
    df = df.join(drivers)
    df = format_standings(df, 'driverId')
    df['Team'] = results.groupby('driverId').Team.last()
    use = ['Position', 'Driver',  'Team', 'points', 'wins', 'podiums', 'scores', 'nationality' ]
    df = df[use].set_index('Position').fillna('')
    df.columns = df.columns.str.capitalize()
    return df

# Constructors championship table
def constructors_standings(df):
    df = df.join(constructors)
    df = format_standings(df, 'constructorId')
    
    # add drivers for team
    tmp = results.join(drivers.drop('number', 1), on='driverId')
    df = df.join(tmp.groupby('constructorId').Driver.unique().str.join(', ').to_frame('Drivers'))

    use = ['Position', 'name', 'points', 'wins', 'podiums', 'scores', 'nationality', 'Drivers' ]
    df = df[use].set_index('Position').fillna('')
    df.columns = df.columns.str.capitalize()
    return df

# Race results table
def format_results(df):
    df['Team'] = df.constructorId.map(constructors.name)
    df['Position'] = df.positionOrder
    df['number'] = df.number.map(int)
    df['points'] = df.points.map(int)
    df.loc[df.points <= 0, 'points'] = ''
    use = ['Driver', 'Team', 'number', 'grid', 'Position', 'points', 'laps', 'time', 'status' ]
    df = df[use].sort_values('Position')
    df = df.fillna('')
    df = df.set_index('Position')
    df.columns = df.columns.str.capitalize()
    return df
plt.rc("figure", figsize=(16, 12))
plt.rc("font", size=(14))
plt.rc("axes", xmargin=0)

display(HTML(
    f'<h1 id="drivers">Formula One Drivers\' World Championship &mdash; {YEAR}</h1>'
))

# Championship position traces
champ = driverStandings.groupby("driverId").position.last().to_frame("Pos")
champ = champ.join(drivers)
order = np.argsort(champ.Pos)

color = [DRIVER_C[d] for d in champ.index[order]]
style = [LINESTYLES[DRIVER_LS[d]] for d in champ.index[order]]
labels = champ.Pos.astype(str) + ". " + champ.display

chart = driverStandings.pivot("raceKey", "driverId", "points")
names = races.set_index("raceKey").reindex(chart.index).name
names = names.str.replace("Grand Prix", "GP").rename("Race")
chart.index = names
chart.columns = labels

# Add origin
row = chart.iloc[0]
chart = pd.concat(((row * 0).to_frame("").T, chart))

chart.iloc[:, order].plot(title=f"F1 Drivers\' World Championship — {YEAR}", color=color, style=style)
plt.xticks(range(chart.shape[0]), chart.index, rotation=45)
plt.grid(axis="x", linestyle="--")
plt.ylabel("Points")
legend_opts = dict(bbox_to_anchor=(1.02, 0, 0.2, 1),
                   loc="upper right",
                   ncol=1,
                   shadow=True,
                   edgecolor="black",
                   mode="expand",
                   borderaxespad=0.)
plt.legend(**legend_opts)
plt.tight_layout()
plt.show()

display(HTML(f"<h2>Results</h2>"))
display(drivers_standings(driverStandings.loc[driverStandings.index.max()].set_index("driverId")).style)
