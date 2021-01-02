import xml.etree.ElementTree as ET
import csv
import pandas as pd
import sys
import time
import os

import helper
from passes import passes
from shots import shots
from goals import goals
from key_events import key_events

# open the XML file - uses the first argument from command line as filename
xml_file_name = sys.argv[1]
date = sys.argv[2]
away_team = sys.argv[3]
home_team = sys.argv[4]
game_ID = (date + away_team + home_team)

# open the the accompanying table CSV files 
players_table = pd.read_csv('players_table.csv')
teams_table = pd.read_csv('teams_table.csv')

# check that inputs are valid (throw error if found)
helper.check_date(date)
helper.check_team_ID(away_team, teams_table)
helper.check_team_ID(home_team, teams_table)

# open the XML file
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

#throw it into a df
events_df = pd.DataFrame(xml_data, columns = ["start", "end", "code", "team", "action", "half", "pos_x", "pos_y"]) 

# the times in the second half in instat are kinda off because it doesn't reset to 45 at the start of the second half 
# here we calculate what the delay is 
second_half_delay_seconds = events_df.loc[events_df['half'] == '2nd half'].iloc[0]['start'] - 45*60

# removing the weird 'start' events in each half
events_df = events_df[events_df.code != 'Start']

# placeholder lists for each of our new columns
event_ID = []
start_time = []
end_time = []
player_ID = []
team_ID = []
half = []
common_axis_pos_x = []
common_axis_pos_y = []

# iterate through each row in the events DF -
# if the event is the the first half - leave the time as-is
# if the event is the the second half, subtract the time delay we calculated earlier
# also find the correct player_ID for each player from the file we opened earlier 
for index, row in events_df.iterrows():
	to_subtract = 0
	if row['half'] == '2nd half':
		to_subtract = second_half_delay_seconds

	row_team_ID = helper.convert_team_name_to_team_ID(row['team'], teams_table)
	row_half = helper.convert_half(row['half'])

	event_ID.append('RAW-' + game_ID + '-' + str(index))
	start_time.append(helper.convert_seconds_to_minutes(row['start'] - to_subtract))
	end_time.append(helper.convert_seconds_to_minutes(row['end'] - to_subtract))
	player_ID.append(helper.convert_code_to_player_ID(row['code'], players_table))
	team_ID.append(row_team_ID)
	half.append(row_half)
	common_axis_pos_x.append(helper.convert_common_axis_pos(row['pos_x'], "x", row_half, row_team_ID, away_team, home_team))
	common_axis_pos_y.append(helper.convert_common_axis_pos(row['pos_y'], "y", row_half, row_team_ID, away_team, home_team))


# add all of the new columns into the DF, and drop the old ones
# doing this individually instead of in place is a lot safer
events_df.drop(['start', 'end', 'code', 'team', 'half'], axis=1, inplace=True)

events_df.insert(loc = 0, column = 'ID', value = event_ID)
events_df.insert(loc = 1, column = 'game_ID', value = [game_ID] * len(events_df.index))
events_df.insert(loc = 2, column = "half", value = half)
events_df.insert(loc = 3, column = "start_time", value = start_time)
events_df.insert(loc = 4, column = "end_time", value = end_time)
events_df.insert(loc = 5, column = "player_ID", value = player_ID)
events_df.insert(loc = 6, column = "team_ID", value = team_ID)
events_df.insert(loc = 10, column = "common_axis_pos_x", value = common_axis_pos_x)
events_df.insert(loc = 11, column = "common_axis_pos_y", value = common_axis_pos_y)

#create a folder to dump the game files in, named after the game_ID
if not os.path.exists(game_ID):
    os.makedirs(game_ID)

# output the DF into a file which is the original filename + events
events_df.to_csv(game_ID + '/raw-events.csv', index=False)
events_df.drop(['common_axis_pos_x', 'common_axis_pos_y'], axis=1, inplace=True)

# run each of the other scripts & output into their own files
passes(pass_df = events_df.copy(), game_ID = game_ID).to_csv(game_ID + "/passes.csv", index=False) 
shots(shot_df = events_df.copy(), game_ID = game_ID).to_csv(game_ID + "/shots.csv", index=False) 
goals(goal_df = events_df.copy(), game_ID = game_ID).to_csv(game_ID + "/goals.csv", index=False) 
key_events(key_event_df = events_df.copy(), game_ID = game_ID).to_csv(game_ID + "/key-events.csv", index=False) 