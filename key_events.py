def key_events(key_event_df, game_ID):
	key_event_df = key_event_df[key_event_df['action'].isin(['Dribbling', 'Dribbles (Successful actions)', 'Dribbles (Unsuccessful actions)', 'Challenges (won)', 'Challenges (lost)', 'Tackles (Successful actions)', 'Tackles (Unsuccessful actions)', 'Picking-ups', 'Fouls', 'Shot on target (saved)'])]
	key_event_df.rename({'ID': 'raw_event_ID'}, axis='columns', inplace=True)
	key_event_df.reset_index(drop=True, inplace=True)
	key_event_ID = []
	for index, row in key_event_df.iterrows():
		key_event_ID.append(game_ID + '-' + str(index))
	key_event_df.insert(loc = 0, column = 'ID', value = key_event_ID)

	successful = []
	for index, row in key_event_df.iterrows():
		if row['action'] == 'Dribbling':
			key_event_df.at[index,'action'] = 'dribble'
			successful.append(1)
		elif row['action'] == 'Dribbles (Successful actions)':
			key_event_df.at[index,'action'] = 'take_on'
			successful.append(1)
		elif row['action'] == 'Dribbles (Unsuccessful actions)':
			key_event_df.at[index,'action'] = 'take_on'
			successful.append(0)
		elif row['action'] == 'Challenges (won)':
			key_event_df.at[index,'action'] = 'challenge'
			successful.append(1)
		elif row['action'] == 'Challenges (lost)':
			key_event_df.at[index,'action'] = 'challenge'
			successful.append(0)
		elif row['action'] == 'Tackles (Successful actions)':
			key_event_df.at[index,'action'] = 'tackle'
			successful.append(1)
		elif row['action'] == 'Tackles (Unsuccessful actions)':
			key_event_df.at[index,'action'] = 'tackle'
			successful.append(0)
		elif row['action'] == 'Picking-ups':
			key_event_df.at[index,'action'] = 'recovery'
			successful.append('null')
		elif row['action'] == 'Fouls':
			key_event_df.at[index,'action'] = 'foul'
			successful.append('null')
		elif row['action'] == 'Shot on target (saved)':
			key_event_df.at[index,'action'] = 'save'
			successful.append('null')
		else:
			successful.append('null')

	key_event_df.insert(loc = 8, column = "successful", value = successful)

	return key_event_df