def passes(pass_df, game_ID): 
    column_suffixes = ['player_ID', 'team_ID', 'pos_x', 'pos_y', 'action', 'start_time', 'end_time']
    shift_column_names = []

    lower_shift_limit = -5
    upper_shift_limit = 10


    #add a bunch of temp columns to each row, each with data we'll need from the the next max_look_ahead # of rows
    for i in range(lower_shift_limit, upper_shift_limit+1): 
        if i != 0:
            for suffix in column_suffixes:
                column_name = str(i) + '_' + suffix
                pass_df[column_name] = pass_df[suffix].shift(-i)
                shift_column_names.append(column_name)

    # of the rows, we only want ones that are passes
    pass_df = pass_df[pass_df['action'].isin(['Passes accurate', 'Passes (inaccurate)', 'Assists'])]
    pass_df.rename({'ID': 'raw_event_ID'}, axis='columns', inplace=True)
    pass_df.reset_index(drop=True, inplace=True)
    pass_ID = []
    for index, row in pass_df.iterrows():
        pass_ID.append(game_ID + '-' + str(index))
    pass_df.insert(loc = 0, column = 'ID', value = pass_ID)

    # setting up the structures for what will hold the data for the receiver
    receiver = []
    successful = []
    end_pos_x = []
    end_pos_y = []
    cross = []

    for index, row in pass_df.iterrows():
        # for reach row in the pass_df 
        # find the first next instance with a different player - we'll take this player as the "receiver"
        # but if it's an assist - just find the next action that's a goal 
        # also if it was a cross, mark the boolean - have to look behind as well as ahead for this one only
        found_next_name = False 
        cross_bool = 0

        y = lower_shift_limit
        while y < upper_shift_limit:
            if y != 0:
                if 'Cross' in str(row[str(y) + '_action']) and row[str(y) + '_player_ID'] == row['player_ID'] and row[str(y) + '_start_time'] == row['start_time'] and row[str(y) + '_end_time'] == row['end_time']:
                    cross_bool = 1
                    break
            y += 1
        
        x = 1
        while x <= upper_shift_limit:
            if row['action'] == 'Assists':
                if row[str(x) + '_action'] == 'Goals': 
                    found_next_name = True
                    receiver.append(row[str(x) + '_player_ID'])
                    successful.append(1) # true
                    end_pos_x.append(row[str(x) + '_pos_x'])
                    end_pos_y.append(row[str(x) + '_pos_y'])
                    cross.append(cross_bool)
                    break
            elif row[str(x) + '_player_ID'] != row['player_ID']:
                if row['action'] == 'Passes accurate' and row['team_ID'] == row[str(x) + '_team_ID']:
                    found_next_name = True
                    receiver.append(row[str(x) + '_player_ID'])
                    successful.append(1) # true
                    end_pos_x.append(row[str(x) + '_pos_x'])
                    end_pos_y.append(row[str(x) + '_pos_y'])
                    cross.append(cross_bool)
                    break
                if row['action'] == 'Passes (inaccurate)' and row['team_ID'] != row[str(x) + '_team_ID']:
                    found_next_name = True
                    receiver.append(row[str(x) + '_player_ID'])
                    successful.append(0) # false
                    # flip the coordinates if it's a turnover
                    end_pos_x.append(round(105 - row[str(x) + '_pos_x'], 1))
                    end_pos_y.append(round(68 - row[str(x) + '_pos_y'], 1))
                    cross.append(cross_bool)
                    break
            x += 1
        #just in case we can't find the receiver
        if (found_next_name == False):
            receiver.append("null")
            end_pos_x.append("null")
            end_pos_y.append("null")
            cross.append(cross_bool)
            if row['action'] == 'Passes accurate':
                successful.append(1) # true
            else:
                successful.append(0) # true

    # add all the lists as their own columns in the df
    pass_df.insert(loc = 10, column = 'successful', value = successful)
    pass_df.insert(loc = 11, column = 'receiver', value = receiver)
    pass_df.insert(loc = 12 ,column = 'end_pos_x', value = end_pos_x)
    pass_df.insert(loc = 13, column = 'end_pos_y', value = end_pos_y)
    pass_df.insert(loc = 14, column = 'cross', value = cross)

    #drop all the temp columns 
    for column in shift_column_names: 
         pass_df.drop([column], axis=1, inplace=True)

    pass_df.rename(columns={'pos_x': 'start_pos_x', 'pos_y': 'start_pos_y'}, inplace=True)
    pass_df.drop(['action'], axis=1, inplace=True)
  
    return pass_df 
