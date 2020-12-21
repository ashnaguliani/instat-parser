def convert_seconds_to_minutes(seconds): 
    minutes, seconds = divmod(seconds, 60)
    return "%d:%02d" % (minutes, seconds) 

def convert_code_to_player_ID(code, players_table):
	instat_name = code.split(" ", 1)[1]
	# player_IDs = players_table.loc[players_table.instat_name==instat_name, 'ID']

	# if len(player_IDs) != 1: 
	# 	raise Exception("Couldn't find '%s' in players table CSV file" % instat_name)
	# 	return "null"
	# else:
	# 	return player_IDs.values[0]
	return instat_name

def convert_team_name_to_team_ID(team_name, teams_table):
	team_IDs = teams_table.loc[teams_table.name==team_name, 'ID']
	if len(team_IDs) != 1: 
		raise Exception("Couldn't find '%s' in teams table CSV file" % team_name)
	else:
		return team_IDs.values[0]

def check_team_ID(team_ID, teams_table):
	team_names = teams_table.loc[teams_table.ID==team_ID, 'name']
	if len(team_names) != 1: 
		raise Exception("Couldn't find '%s' in teams table CSV file" % team_ID)