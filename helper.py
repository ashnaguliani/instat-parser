def convert_seconds_to_minutes(seconds): 
    minutes, seconds = divmod(seconds, 60)
    return "%d:%02d" % (minutes, seconds) 