def convert_seconds_to_minutes(seconds): 
    minutes, seconds = divmod(seconds, 60)
    return "%d:%02d" % (minutes, seconds) 

def convert_code_to_player_ID(code, players_table):
	instat_name = code.split(" ", 1)[1]
	player_IDs = players_table.loc[players_table.instat_name==instat_name, 'ID']

	if len(player_IDs) != 1: 
		raise Exception("Couldn't find '%s' in players table CSV file" % instat_name)
		return "\N"
	else:
		return player_IDs.values[0]
	# return instat_name

def convert_team_name_to_team_ID(team_name, teams_table):
	team_IDs = teams_table.loc[teams_table.name==team_name, 'ID']
	if len(team_IDs) != 1: 
		raise Exception("Couldn't find '%s' in teams table CSV file" % team_name)
	else:
		return team_IDs.values[0]

def convert_half(half_str):
	if half_str == '1st half':
		return 1
	elif half_str == '2nd half':
		return 2
	elif half_str == '1st extra time':
		return 3 
	elif half_str == '2nd extra time':
		return 4
	else:
		if half_str != 'Penalty shooot-out':
			print("couldn't parse '%s' - if this game didn't go to PKs check XML vs code" % half_str)
		return 5

def convert_common_axis_pos(pos, x_or_y, half, team, away_team, home_team):
	flipped = flip(pos, x_or_y)

	if (half in (1, 3) and team == away_team) or (half in (2, 4) and team == home_team):
		return flipped
	else:
		return pos

def flip(pos, x_or_y):
	if x_or_y == "x":
		flipped = round(105 - pos, 1)
	elif x_or_y == "y": 
		flipped = round(68 - pos, 1)
	return flipped
	
def check_team_ID(team_ID, teams_table):
	team_names = teams_table.loc[teams_table.ID==team_ID, 'name']
	if len(team_names) != 1: 
		raise Exception("Couldn't find '%s' in teams table CSV file" % team_ID)

def check_date(date): 
	if len(date) != 8 or date.isdigit() == False:
		raise Exception("Date '%s' should have 8 digits in format YYYYMMDD" % date)

	year = date[:4]
	month = date[4:6]
	day = date[6:]

	if int(month) > 12: 
		raise Exception("Date '%s' (YYYYMMDD) should have month between 01-12" % date)
	elif int(day) > 31:
		raise Exception("Date '%s' (YYYYMMDD) should have day between 01-31" % date)

def out_of_bounds(pos_x, pos_y):
	out_of_bounds = False

	if pos_x == 0.0 or pos_x == 105.0:
		out_of_bounds = True
	if pos_y in (0.0, 68.0):
		out_of_bounds = True

	return out_of_bounds



