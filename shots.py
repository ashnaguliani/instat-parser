def shots(shot_df): 
    max_shift = 3

    column_suffixes = ['player', 'action', 'start_time', 'end_time']
    shift_column_names = []

    for i in range(-(max_shift), max_shift+1): 
        if i != 0: 
            for suffix in column_suffixes:
                column_name = str(i) + '_' + suffix
                shot_df[column_name] = shot_df[suffix].shift(-i)
                shift_column_names.append(column_name)

    shot_df = shot_df[shot_df['action'].isin(['Shots'])]

    # goal_scored = []
    accuracy = []

    for index, row in shot_df.iterrows():
        x = -max_shift
        accuracy_row = "blocked"
        while x <= max_shift:
            if x != 0:
                if row[str(x) + '_player'] == row['player'] and row[str(x) + '_start_time'] == row['start_time'] and row[str(x) + '_end_time'] == row['end_time']:

                    if row[str(x) + '_action'] == 'Shot on target': 
                        accuracy_row = "on_target"
                    elif row[str(x) + '_action'] == 'Shot into the bar/post': 
                        accuracy_row = "post_crossbar"
                    elif row[str(x) + '_action'] == 'Wide shot':
                        accuracy_row = "wide" 
            x += 1
        accuracy.append(accuracy_row)

    shot_df.insert(loc = 10, column = "accuracy", value = accuracy)

    shot_df.insert(loc = 0, column = 'raw_event_ID', value = shot_df.index)
    shot_df.reset_index(drop=True, inplace=True)

    for column in shift_column_names: 
         shot_df.drop([column], axis=1, inplace=True)
    return(shot_df)