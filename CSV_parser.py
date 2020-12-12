import pandas as pd
import sys
import time

from helper import convert_seconds_to_minutes, convert_code_to_playerID
from passes import passes
from shots import shots
from goals import goals
from key_events import key_events

# last highest ID in events table - so that the IDs don't overlap with what's already in the DB
index_to_increase = 0

# open the CSV file - uses the first argument from command line as filename
csv_file_name = sys.argv[1]
events_df = pd.read_csv(csv_file_name, index_col=0)
events_df.index += index_to_increase

# open the players table CSV file with all the players' names & IDs
players_table = pd.read_csv('players_table.csv')

# the times in the second half in instat are kinda off - here we calculate what the delay is 
second_half_delay_seconds = events_df.loc[events_df['half'] == '2nd half'].iloc[0]['start'] - 45*60

# removing the weird 'start' events in each half
events_df = events_df[events_df.code != 'Start']

# placeholder lists for each of our new columns
start_time = []
end_time = []
player_ID = []

# iterate through each row in the events DF -
# if the event is the the first half - leave the time as-is
# if the event is the the second half, subtract the time delay we calculated earlier
# also find the correct player_ID for each player from the file we opened earlier 
for index, row in events_df.iterrows():
    to_subtract = 0
    if row['half'] == '2nd half':
        to_subtract = second_half_delay_seconds

    start_time.append(convert_seconds_to_minutes(row['start'] - to_subtract))
    end_time.append(convert_seconds_to_minutes(row['end'] - to_subtract))
    player_ID.append(convert_code_to_playerID(row['code'], players_table))

# add all of the new columns into the DF, and drop the old ones
# doing this individually instead of in place is a lot safer
events_df.insert(loc = 1, column = "start_time", value = start_time)
events_df.insert(loc = 2, column = "end_time", value = end_time)
events_df.insert(loc = 3, column = "player_ID", value = player_ID)
events_df.drop(['start', 'end', 'code'], axis=1, inplace=True)

# output the DF into a file which is the original filename + events
events_df.to_csv(csv_file_name.split('.')[0] + "-events.csv")

# run each of the other scripts & output into their own files
passes(pass_df = events_df.copy()).to_csv(csv_file_name.split('.')[0] + "-passes.csv") 
shots(shot_df = events_df.copy()).to_csv(csv_file_name.split('.')[0] + "-shots.csv") 
goals(goal_df = events_df.copy()).to_csv(csv_file_name.split('.')[0] + "-goals.csv") 
key_events(key_event_df = events_df.copy()).to_csv(csv_file_name.split('.')[0] + "-key-events.csv") 