#!/usr/bin/env python
import datetime
import numpy as np

'''
A subclass of the Exception class to handle bad increment input in the daterange generator
'''
class DateRangeNotSupported(Exception):
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return 'Time increment of "%s" not supported. Increment can be \'hours\', \'days\' or \'minutes\'.'%self.code

'''
A generator that iterates over a series of sequential datetimes with the specified increment.
Can handle increments of 'hours', 'days', or 'minutes'.
'''
def daterange(start_date, end_date, increment='hours'):
    if increment == 'minutes':
        day_multiple = 24.0 * 60.0
    elif increment == 'days':
        day_multiple = 1.0
    elif increment == 'hours':
        day_multiple = 24.0
    else:
        raise DateRangeNotSupported(increment)

    for n in np.arange(((end_date - start_date).days + 1) * day_multiple):
        yield start_date.replace(hour=0,minute=0,second=0) + datetime.timedelta(**{increment:n})

'''
A class that accepts login timestamps and returns forecasts for a given hour and day of the week.
TODO: Error checking.
'''
class DemandPredictor(object):
    def __init__(self):
        # Login counts per day per hour.
        self.login_counts = np.zeros((7,24))
        # The number of hours for each day that have elapsed. This is
        # the denominator of the average we will return.
        self.day_counts = np.zeros((7,24))
        # This is where we store incomplete hours. Once the hour is
        # complete this is emptied out.
        self.login_counts_tmp = np.zeros((7,24))
        # The last timestamp recieved.
        self.last_timestamp = None

    def addLogin(self, timestamp):
        # Update the temporary login counts.
        self.login_counts_tmp[timestamp.weekday(), timestamp.hour] += 1.0
        # If this is the first timestamp we will have no previous one.
        if self.last_timestamp is None:
            self.last_timestamp = timestamp
        # Check if we are in a new day. This is how we update the day counts for
        # the denominator of the forecast.
        self.check_day(timestamp)

    def check_day(self, timestamp):
        # Is the new timestamp in a new day?
        if not (timestamp.date() == self.last_timestamp.date() and timestamp.hour == self.last_timestamp.hour):
            hour_difference = timestamp.hour - self.last_timestamp.hour
            # If the new timestamp skipped hours we still need to count them
            # to get a good average.
            if hour_difference > 1.0 or hour_difference < -23.0:
                for n in range(int(hour_difference) - 1):
                    missed_hour = self.last_timestamp + datetime.timedelta(**{'hours':n + 1})
                    self.day_counts[missed_hour.weekday(), missed_hour.hour] += 1.0
                self.day_counts[self.last_timestamp.weekday(), self.last_timestamp.hour] += 1.0
                self.login_counts[self.last_timestamp.weekday(), self.last_timestamp.hour] += self.login_counts_tmp[self.last_timestamp.weekday(), self.last_timestamp.hour]
                self.login_counts_tmp[self.last_timestamp.weekday(), self.last_timestamp.hour] = 0.0
            else:
                self.day_counts[self.last_timestamp.weekday(), self.last_timestamp.hour] += 1.0
                self.login_counts[self.last_timestamp.weekday(), self.last_timestamp.hour] += self.login_counts_tmp[self.last_timestamp.weekday(), self.last_timestamp.hour]
                self.login_counts_tmp[self.last_timestamp.weekday(), self.last_timestamp.hour] = 0.0
        self.last_timestamp = timestamp

    def forecast(self, day, hour):
        # Return the forecast or '-' if we haven't collected enough data.
        if self.day_counts[day, hour] != 0:
            return self.login_counts[day, hour] / self.day_counts[day, hour]
        else:
            return '-'



