import pandas as pd
import sys

def pass_parser(pass_df, max_shift): 
    column_suffixes = ['code', 'pos_x', 'pos_y', 'action']
    shift_column_names = []

    #add a bunch of temp columns to each row, each with data we'll need from the the next max_shift # of rows
    for i in range(1, max_shift+1): 
        for suffix in column_suffixes:
            column_name = str(i) + '_' + suffix
            pass_df[column_name] = pass_df[suffix].shift(-i)
            shift_column_names.append(column_name)

    # of the rows, we only want ones that are passes
    mask = pass_df['action'].isin(['Passes accurate', 'Passes (inaccurate)', 'Assists'])
    pass_df = pass_df[mask]

    # setting up the structure for what will hold our data of the recipient - a list of lists
    # these are: code (player), successful (boolean t/f), pos_x, pos_y
    recipient = []
    successful = []
    end_pos_x = []
    end_pos_y = []

    # for reach row in the pass_df 
    for index, row in pass_df.iterrows():
        # find the first next instance with a different player - we'll take this player as the "recipient"
        # but if it's an assist - just find the next action that's a goal 
        x = 1
        found_next_name = False 
        while x <= max_shift:
            if row['action'] == 'Assists':
                if row[str(x) + '_action'] == 'Goals': 
                    found_next_name = True
                    recipient.append(row[str(x) + '_code'])
                    successful.append(1) # true
                    end_pos_x.append(row[str(x) + '_pos_x'])
                    end_pos_y.append(row[str(x) + '_pos_y'])
                    break
            elif row[str(x) + '_code'] != row['code']:
                found_next_name = True
                if row['action'] == 'Passes accurate':
                    recipient.append(row[str(x) + '_code'])
                    successful.append(1) # true
                    end_pos_x.append(row[str(x) + '_pos_x'])
                    end_pos_y.append(row[str(x) + '_pos_y'])
                else:
                    recipient.append(row[str(x) + '_code'])
                    successful.append(0) # false
                    # flip the coordinates if it's a turnover
                    end_pos_x.append(round(105 - row[str(x) + '_pos_x'], 1))
                    end_pos_y.append(round(68 - row[str(x) + '_pos_y'], 1))
                break
            x += 1

    pass_df.loc[:,'recipient'] = recipient
    pass_df.loc[:,'successful'] = successful
    pass_df.loc[:,'end_pos_x'] = end_pos_x
    pass_df.loc[:,'end_pos_y'] = end_pos_y

    #drop all the temp columns 
    for column in shift_column_names: 
         pass_df.drop([column], axis=1, inplace=True)

    pass_df.rename(columns={'start': 'start_time', 'end': 'end_time', 'code': 'player', 'pos_x': 'start_pos_x', 'pos_y': 'start_pos_y'}, inplace=True)
    pass_df.drop(['action'], axis=1, inplace=True)
    return pass_df 


def shot_parser(shot_df, max_shift): 
    column_suffixes = ['code','action']
    shift_column_names = []

    for i in range(-(max_shift), max_shift+1): 
        if i != 0: 
            for suffix in column_suffixes:
                column_name = str(i) + '_' + suffix
                shot_df[column_name] = shot_df[suffix].shift(-i)
                shift_column_names.append(column_name)

    shot_df = shot_df[shot_df['action'].isin(['Shots', 'Goals'])]

    goal = []
    on_target = []
    wide = []
    bar_post = []

    for index, row in shot_df.iterrows():
        x = -max_shift
        goal_row = False 
        on_target_row = False
        wide_row = False
        bar_post_row = False

        if row['action'] == 'Goals':
            goal_row = True
            on_target_row = True
        else: 
            while x <= max_shift:
                if x != 0:
                    if row[str(x) + '_code'] == row['code']: 
                        if row[str(x) + '_action'] == 'Shot on target': 
                            on_target_row = True
                        if row[str(x) + '_action'] == 'Shot into the bar/post': 
                            bar_post_row = True
                        if row[str(x) + '_action'] == 'Wide shot':
                            wide_row = True
                x += 1
            
        goal.append(goal_row)
        on_target.append(on_target_row) 
        wide.append(wide_row)
        bar_post.append(bar_post_row)   
        
    shot_df.loc[:,'goal'] = goal
    shot_df.loc[:,'on_target'] = on_target
    shot_df.loc[:,'wide'] = wide
    shot_df.loc[:,'bar_post'] = bar_post

    for column in shift_column_names: 
         shot_df.drop([column], axis=1, inplace=True)
    return(shot_df)

# open the CSV file - uses the first argument from command line as filename
csv_file_name = sys.argv[1]
df = pd.read_csv(csv_file_name, index_col=0)
df = df[df.code != 'Start']

# output to a file (original file name + "-passes.csv")
pass_parser(pass_df = df.copy(), max_shift = 10).to_csv(csv_file_name.split('.')[0] + "-passes.csv", index=False) 
shot_parser(shot_df = df.copy(), max_shift = 3).to_csv(csv_file_name.split('.')[0] + "-shots.csv", index=False) 
