def passes(pass_df): 
    column_suffixes = ['player_ID', 'team', 'pos_x', 'pos_y', 'action', 'start_time', 'end_time']
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
    pass_df = pass_df[pass_df['action'].isin(['Passes accurate', 'Passes (inaccurate)', 'Assists', 'Crosses (inaccurate)'])]

    # setting up the structures for what will hold the data for the receiver
    receiver = []
    successful = []
    end_pos_x = []
    end_pos_y = []
    cross = []
    cross_blocked = []

    
    for index, row in pass_df.iterrows():
        y = lower_shift_limit
        while y < upper_shift_limit:
            if y != 0:
                if row[str(y) + '_player_ID'] == row['player_ID'] and row[str(y) + '_start_time'] == row['start_time'] and row[str(y) + '_end_time'] == row['end_time'] and row[str(y) + '_action'] == 'Passes (inaccurate)':
                    pass_df.drop(index, inplace=True)
                    break
            y += 1

    for index, row in pass_df.iterrows():
        # for reach row in the pass_df 
        # find the first next instance with a different player - we'll take this player as the "receiver"
        # but if it's an assist - just find the next action that's a goal 
        # also if it was a cross, mark the boolean - have to look behind as well as ahead for this one only
        cross_bool = 0
        found_next_name = False 

        y = lower_shift_limit
        while y < upper_shift_limit:
            if y != 0:
                if row[str(y) + '_player_ID'] == row['player_ID'] and 'Cross' in row[str(y) + '_action'] and row[str(y) + '_start_time'] == row['start_time'] and row[str(y) + '_end_time'] == row['end_time']:
                    cross_bool = 1
                    break
                if row[str(y) + '_player_ID'] != row['player_ID'] and row['action'] == 'Crosses (inaccurate)' and row[str(y) + '_start_time'] == row['start_time'] and row[str(y) + '_end_time'] == row['end_time']: 
                    found_next_name = True
                    receiver.append(row[str(y) + '_player_ID'])
                    successful.append(0)
                    end_pos_x.append(row[str(y) + '_pos_x'])
                    end_pos_y.append(row[str(y) + '_pos_y'])
                    cross.append(1)
                    cross_blocked.append(1)
                    break
            y += 1
        
        x = 1
        while x <= upper_shift_limit:
            if row['action'] != 'Crosses (inaccurate)':
                if row['action'] == 'Assists':
                    if row[str(x) + '_action'] == 'Goals': 
                        found_next_name = True
                        receiver.append(row[str(x) + '_player_ID'])
                        successful.append(1) # true
                        end_pos_x.append(row[str(x) + '_pos_x'])
                        end_pos_y.append(row[str(x) + '_pos_y'])
                        cross.append(cross_bool)
                        cross_blocked.append(0)
                        break
                elif row[str(x) + '_player_ID'] != row['player_ID']:
                    if row['action'] == 'Passes accurate' and row['team'] == row[str(x) + '_team']:
                        found_next_name = True
                        receiver.append(row[str(x) + '_player_ID'])
                        successful.append(1) # true
                        end_pos_x.append(row[str(x) + '_pos_x'])
                        end_pos_y.append(row[str(x) + '_pos_y'])
                        cross.append(cross_bool)
                        cross_blocked.append(0)
                        break
                    if row['action'] == 'Passes (inaccurate)' and row['team'] != row[str(x) + '_team']:
                        found_next_name = True
                        receiver.append(row[str(x) + '_player_ID'])
                        successful.append(0) # false
                        # flip the coordinates if it's a turnover
                        end_pos_x.append(round(105 - row[str(x) + '_pos_x'], 1))
                        end_pos_y.append(round(68 - row[str(x) + '_pos_y'], 1))
                        cross.append(cross_bool)
                        cross_blocked.append(0)
                        break
            x += 1
        if (found_next_name == False):
            if row['action'] == 'Passes accurate':
                receiver.append("null")
                successful.append(1) # true
                end_pos_x.append("null")
                end_pos_y.append("null")
                cross.append(cross_bool)
                cross_blocked.append(0)
            else:
                receiver.append("null")
                successful.append(0) # true
                end_pos_x.append("null")
                end_pos_y.append("null")
                cross.append(cross_bool)
                cross_blocked.append(0)

    # add all the lists as their own columns in the df
    pass_df.insert(loc = 9, column = 'successful', value = successful)
    pass_df.insert(loc = 10, column = 'receiver', value = receiver)
    pass_df.insert(loc = 11 ,column = 'end_pos_x', value = end_pos_x)
    pass_df.insert(loc = 12, column = 'end_pos_y', value = end_pos_y)
    pass_df.insert(loc = 13, column = 'cross', value = cross)
    pass_df.insert(loc = 14, column = 'cross_blocked', value = cross_blocked)

    #drop all the temp columns 
    for column in shift_column_names: 
         pass_df.drop([column], axis=1, inplace=True)

    pass_df.rename(columns={'pos_x': 'start_pos_x', 'pos_y': 'start_pos_y'}, inplace=True)
    pass_df.drop(['action'], axis=1, inplace=True)

    pass_df.insert(loc = 0, column = 'raw_event_ID', value = pass_df.index)
    pass_df.reset_index(drop=True, inplace=True)
    return pass_df 
