import numpy as np
from dateutil import parser
from datetime import datetime, timedelta

def shift_date(list_of_dates):
    start_date = parser.parse("01/01/2019")
    end_date = parser.parse("01/01/2020")
    range_of_dates = np.arange(start_date, end_date, timedelta(days=1)) # span = 1 year
    range_of_dates = [*range_of_dates, *range_of_dates] # span = 2 years
    range_of_dates = [parser.parse(str(x)).strftime("%m/%d") for x in np.datetime_as_string(range_of_dates)] # new format mm/dd

    # save location of match days over range_of_days
    locations = []
    length = len(list_of_dates)
    sorted_list = sorted(list_of_dates)
    for i in range(len(range_of_dates)):
        for x in sorted_list:
            if range_of_dates[i] == x:
                locations.append(i)

    diffs = [locations[i + 1] - locations[i] for i in range(length)]
    while np.argmax(diffs) < length-1: # till the optimal choice is reached
        locations = [locations[-1], *locations[:-1]] # shift element orders by 1 (last element comes to first order)
        diffs = [abs(locations[i + 1] - locations[i]) for i in range(length)] # calculate new differences

    start, end = locations[0], locations[length-1]
    return range_of_dates[start:end+1] # return the optimal choice