import xml.etree.ElementTree as ET
import csv
import pandas as pd
import sys
import time
import os

from helper import convert_seconds_to_minutes, convert_code_to_playerID
from passes import passes
from shots import shots
from goals import goals
from key_events import key_events

# open the XML file - uses the first argument from command line as filename
xml_file_name = sys.argv[1]
tree = ET.parse(xml_file_name)
root = tree.getroot()

xml_data = []

# we want to look through each "instance" in the XML file
for elem in tree.findall('.//instance'):
# create an empty list to store all the data for this instance
	instance = []
	instance.append(float(elem.find('start').text))
	instance.append(float(elem.find('end').text))
	instance.append(elem.find('code').text)
	# there's a couple instances that don't have every variable - here we'll check that the
	# instance does have at least one of them (so we'll assume it has all the rest) to make 
	# sure that doing a get is safe
	if elem.find('label') is not None:
		instance.append(elem[4][1].text)
		instance.append(elem[5][1].text)
		instance.append(elem[6][1].text)
		instance.append(float(elem.find('pos_x').text))
		instance.append(float(elem.find('pos_y').text))

	# write the row to the file
	xml_data.append(instance)

events_df = pd.DataFrame(xml_data, columns = ["start", "end", "code", "team", "action", "half", "pos_x", "pos_y"]) 

# last highest ID in events table - so that the IDs don't overlap with what's already in the DB
index_to_increase = 0 #sys.argv[2]
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

sub_directory = xml_file_name.split('.')[0]
if not os.path.exists(sub_directory):
    os.makedirs(sub_directory)

# output the DF into a file which is the original filename + events
events_df.to_csv(sub_directory + '/events.csv')

# run each of the other scripts & output into their own files
passes(pass_df = events_df.copy()).to_csv(sub_directory + "/passes.csv") 
shots(shot_df = events_df.copy()).to_csv(sub_directory + "/shots.csv") 
goals(goal_df = events_df.copy()).to_csv(sub_directory + "/goals.csv") 
key_events(key_event_df = events_df.copy()).to_csv(sub_directory + "/key-events.csv") 