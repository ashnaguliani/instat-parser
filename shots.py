def shots(shot_df, game_ID): 
    max_shift = 7

    column_suffixes = ['player_ID', 'action', 'start_time', 'end_time', 'pos_x', 'pos_y']
    shift_column_names = []

    for i in range(-(max_shift), max_shift+1): 
        if i != 0: 
            for suffix in column_suffixes:
                column_name = str(i) + '_' + suffix
                shot_df[column_name] = shot_df[suffix].shift(-i)
                shift_column_names.append(column_name)

    shot_df = shot_df[shot_df['action'].isin(['Shots', 'Goals'])]
    shot_df = shot_df[shot_df['half'].isin([1, 2, 3])]

    # right now our DF includes own goals - let's drop those because they're not shots 
    for index, row in shot_df.iterrows():
        if row['action'] == 'Goals':
            y = -max_shift
            while y < max_shift:
                if y != 0:
                    if row[str(y) + '_action'] == 'Own goal' and row[str(y) + '_player_ID'] == row['player_ID'] and row[str(y) + '_start_time'] == row['start_time'] and row[str(y) + '_end_time'] == row['end_time']:
                        shot_df.drop(index, inplace=True)
                        break
                y += 1

    shot_df.rename({'ID': 'raw_event_ID'}, axis='columns', inplace=True)
    shot_df.reset_index(drop=True, inplace=True)
    shot_ID = []
    for index, row in shot_df.iterrows():
        shot_ID.append('SHOT-' + game_ID + '-' + str(index))
    shot_df.insert(loc = 0, column = 'ID', value = shot_ID)

    # filter through each shot attempt - if it was on target, wide, or bar/post there will be another action that describes that
    # if none of those, we can assume it was blocked (checked over a bunch of games this seems to hold true)
    # unless it was a goal - then we assume on_target
    accuracy = []
    penalty = []
    for index, row in shot_df.iterrows():
        x = -max_shift
        penalty_row = 0
        if row['action'] == 'Goals':
            accuracy_row = 'on_target'
        else:
            accuracy_row = "blocked"
        while x <= max_shift:
            if x != 0:
                if row[str(x) + '_player_ID'] == row['player_ID'] and row[str(x) + '_pos_x'] == row['pos_x'] and row[str(x) + '_pos_y'] == row['pos_y']:
                    if row[str(x) + '_action'] == 'Penalty':    
                        penalty_row = 1
                    elif row[str(x) + '_action'] == 'Shot on target': 
                        accuracy_row = "on_target"
                    elif row[str(x) + '_action'] == 'Shot into the bar/post': 
                        accuracy_row = "post_crossbar"
                    elif row[str(x) + '_action'] == 'Wide shot':
                        accuracy_row = "wide" 
            x += 1
        accuracy.append(accuracy_row)
        penalty.append(penalty_row)

    # add the accuracy column & drop the placeholder columns (also actions because they're all shots)
    shot_df.insert(loc = 11, column = "accuracy", value = accuracy)
    shot_df.insert(loc = 12, column = "penalty", value = penalty)
    shot_df.drop('action', axis=1, inplace=True)
    for column in shift_column_names: 
        shot_df.drop([column], axis=1, inplace=True)

    return(shot_df)