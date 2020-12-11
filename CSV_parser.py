import pandas as pd
import sys
import time

from helper import convert_seconds_to_minutes
from passes import passes
from shots import shots
from goals import goals
from key_events import key_events

# last highest ID in events table
index_to_increase = 0

# open the CSV file - uses the first argument from command line as filename
csv_file_name = sys.argv[1]
events_df = pd.read_csv(csv_file_name, index_col=0)
events_df.index += index_to_increase

second_half_delay_seconds = events_df.loc[events_df['half'] == '2nd half'].iloc[0]['start'] - 45*60

events_df = events_df[events_df.code != 'Start']
events_df.rename(columns={'code': 'player'}, inplace=True)

start_time = []
end_time = []
for index, row in events_df.iterrows():
    to_subtract = 0
    if row['half'] == '2nd half':
        to_subtract = second_half_delay_seconds
    start_time.append(convert_seconds_to_minutes(row['start'] - to_subtract))
    end_time.append(convert_seconds_to_minutes(row['end'] - to_subtract))

events_df.insert(loc = 1, column = "start_time", value = start_time)
events_df.insert(loc = 2, column = "end_time", value = end_time)
events_df.drop(['start', 'end'], axis=1, inplace=True)
events_df.to_csv(csv_file_name.split('.')[0] + "-events.csv")


passes(pass_df = events_df.copy()).to_csv(csv_file_name.split('.')[0] + "-passes.csv") 
shots(shot_df = events_df.copy()).to_csv(csv_file_name.split('.')[0] + "-shots.csv") 
goals(goal_df = events_df.copy()).to_csv(csv_file_name.split('.')[0] + "-goals.csv") 
key_events(key_event_df = events_df.copy()).to_csv(csv_file_name.split('.')[0] + "-key-events.csv") 