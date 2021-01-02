def goals(goal_df, game_ID):
	max_shift = 6

	column_suffixes = ['player_ID', 'action', 'team_ID', 'pos_x', 'pos_y']
	shift_column_names = []

	for i in range(-(max_shift), max_shift+1): 
		if i != 0: 
			for suffix in column_suffixes:
				column_name = str(i) + '_' + suffix
				goal_df[column_name] = goal_df[suffix].shift(-i)
				shift_column_names.append(column_name)

	goal_df = goal_df[goal_df['action'].isin(['Goals', 'Own goal'])]
	goal_df = goal_df[goal_df['half'].isin([1, 2, 3])]

    # right now our DF includes own goals twice (as a goal event and an OG event) - let's drop one of those (the regular goal one)
	for index, row in goal_df.iterrows():
		if row['action'] == 'Goals':
			y = -max_shift
			while y < max_shift:
				if y != 0:
					if row[str(y) + '_action'] == 'Own goal' and row[str(y) + '_player_ID'] == row['player_ID'] and row[str(y) + '_pos_x'] == row['pos_x'] and row[str(y) + '_pos_y'] == row['pos_y']:
						goal_df.drop(index, inplace=True)
						break
				y += 1

	goal_df.rename({'ID': 'raw_event_ID'}, axis='columns', inplace=True)
	goal_df.reset_index(drop=True, inplace=True)
	goal_ID = []
	for index, row in goal_df.iterrows():
		goal_ID.append('GOAL' + game_ID + '-' + str(index))
	goal_df.insert(loc = 0, column = 'ID', value = goal_ID)

	assisted_by = []
	assist_pos_x = []
	assist_pos_y = []
	conceding_GK = []
	conceding_team = []
	own_goal = []
	penalty = []

	for index, row in goal_df.iterrows():
		assisted_by_row = "\N"
		assist_pos_x_row = "\N"
		assist_pos_y_row = "\N"
		conceding_GK_row = "\N"
		conceding_team_row = "\N"
		penalty_row = 0
		
		x = -max_shift
		while x <= max_shift:
			if x != 0:
				if row[str(x) + '_action'] == 'Penalty' and row[str(x) + '_player_ID'] == row['player_ID'] and row[str(x) + '_pos_x'] == row['pos_x'] and row[str(x) + '_pos_y'] == row['pos_y']:
					penalty_row = 1
				elif row[str(x) + '_action'] == 'Goals conceded':
					conceding_GK_row = row[str(x) + '_player_ID']
					conceding_team_row = row[str(x) + '_team_ID']
				elif row[str(x) + '_action'] == 'Assists':
					assisted_by_row = row[str(x) + '_player_ID']
					assist_pos_x_row = row[str(x) + '_pos_x']
					assist_pos_y_row = row[str(x) + '_pos_y']
			x += 1

		assisted_by.append(assisted_by_row)
		assist_pos_x.append(assist_pos_x_row)
		assist_pos_y.append(assist_pos_y_row)
		conceding_GK.append(conceding_GK_row)
		conceding_team.append(conceding_team_row)
		penalty.append(penalty_row)
		
		if row['action'] == 'Own goal':
			own_goal.append(1)
		else:
			own_goal.append(0)


	goal_df.insert(loc = 11, column = "assisted_by", value = assisted_by)
	goal_df.insert(loc = 12, column = "assist_pos_x", value = assist_pos_x)
	goal_df.insert(loc = 13, column = "assist_pos_y", value = assist_pos_y)
	goal_df.insert(loc = 14, column = "conceding_GK", value = conceding_GK)
	goal_df.insert(loc = 15, column = "conceding_team", value = conceding_team)
	goal_df.insert(loc = 16, column = "penalty", value = penalty)
	goal_df.insert(loc = 17, column = "own_goal", value = own_goal)

	goal_df.drop('action', axis=1, inplace=True)
	
	for column in shift_column_names: 
		goal_df.drop([column], axis=1, inplace=True)

	return goal_df