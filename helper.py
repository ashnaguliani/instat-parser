def convert_seconds_to_minutes(seconds): 
    minutes, seconds = divmod(seconds, 60)
    return "%d:%02d" % (minutes, seconds) 

def convert_code_to_playerID(code, players_table):
	instat_name = code.split(" ", 1)[1]
	# player_IDs = players_table.loc[players_table.instat_name==instat_name, 'player_ID']

	# if len(player_IDs) != 1: 
	# 	print("Couldn't find '%s' in players table CSV file" % instat_name)
	# 	return "null"
	# else:
	# 	return player_IDs.values[0]
	return instat_name