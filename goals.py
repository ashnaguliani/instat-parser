def goals(goal_df):
	max_shift = 3

	column_suffixes = ['player', 'action', 'team', 'pos_x', 'pos_y']
	shift_column_names = []

	for i in range(-(max_shift), max_shift+1): 
		if i != 0: 
			for suffix in column_suffixes:
				column_name = str(i) + '_' + suffix
				goal_df[column_name] = goal_df[suffix].shift(-i)
				shift_column_names.append(column_name)

	goal_df = goal_df[goal_df['action'].isin(['Goals'])]


	assisted_by = []
	assist_pos_x = []
	assist_pos_y = []
	conceding_GK = []
	conceding_team = []

	for index, row in goal_df.iterrows():
		assisted_by_row = "null"
		assist_pos_x_row = "null"
		assist_pos_y_row = "null"
		conceding_GK_row = "null"
		conceding_team_row = "null"

		x = -max_shift
		while x <= max_shift:
			if x != 0:
				if row[str(x) + '_action'] == 'Goals conceded':
					conceding_GK_row = row[str(x) + '_player']
					conceding_team_row = row[str(x) + '_team']
				elif row[str(x) + '_action'] == 'Assists':
					assisted_by_row = row[str(x) + '_player']
					assist_pos_x_row = row[str(x) + '_pos_x']
					assist_pos_y_row = row[str(x) + '_pos_y']
			x += 1

		assisted_by.append(assisted_by_row)
		assist_pos_x.append(assist_pos_x_row)
		assist_pos_y.append(assist_pos_y_row)
		conceding_GK.append(conceding_GK_row)
		conceding_team.append(conceding_team_row)

	goal_df.insert(loc = 9, column = "assisted_by", value = assisted_by)
	goal_df.insert(loc = 10, column = "assist_pos_x", value = assist_pos_x)
	goal_df.insert(loc = 11, column = "assist_pos_y", value = assist_pos_y)
	goal_df.insert(loc = 12, column = "conceding_GK", value = conceding_GK)
	goal_df.insert(loc = 13, column = "conceding_team", value = conceding_team)

	goal_df.insert(loc = 0, column = 'raw_event_ID', value = goal_df.index)
	goal_df.reset_index(drop=True, inplace=True)
	
	for column in shift_column_names: 
		goal_df.drop([column], axis=1, inplace=True)

	return goal_df