#!/usr/bin/env python
import json
import dateutil.parser
import datetime
import numpy as np
import calendar
import time
import os
import sys
import itertools
import cPickle
import site
import math

import Uber
site.addsitedir('/Users/sachs/Documents/VirtualCalifornia/trunk/vcal_py/')
import Chaos

def login_rate(data, increment='hours'):
    
    f = open(data,'r')
    logins = json.loads(f.read())
    f.close()

    logins_np = np.array([dateutil.parser.parse(x) for x in logins], dtype=datetime.datetime)
    
    #rate = np.empty((len(list(daterange(logins_np[0], logins_np[-1], increment=increment)))),
    #                            dtype=np.dtype({'names':['time','count'],'formats':[datetime.datetime,'i']}))
    rate = []
    
    
    login_index = 0
    for range_index, single_date in enumerate(Uber.daterange(logins_np[0], logins_np[-1], increment=increment)):
        hour_count = {'time':single_date, 'count':0}
        #rate[range_index]['time'] = single_date
        #rate[range_index]['count'] = 0
        try:
            while logins_np[login_index] < single_date + datetime.timedelta(**{increment:1}):
                hour_count['count'] += 1
                #rate[range_index]['count'] += 1
                login_index += 1
        except IndexError:
            pass
        rate.append(hour_count)

    return rate

def ave_rate(data):
    f = open(data,'r')
    logins = json.loads(f.read())
    f.close()

    logins_np = np.array([dateutil.parser.parse(x) for x in logins], dtype=datetime.datetime)
    
    counts = np.zeros((7,24,2))
    
    curr_date = logins_np[0].date()
    counts[logins_np[0].weekday(), 0:24, 1] += 1.0
    for login in logins_np:
        counts[login.weekday(), login.hour, 0] += 1.0
        #print login.weekday(), login.date(), curr_date,
        if login.date() != curr_date:
            counts[login.weekday(), 0:24, 1] += 1.0
            curr_date = login.date()
        #print curr_date

    aves = np.zeros((7,24,1))
    
    it = np.nditer(aves, flags=['multi_index'])
    while not it.finished:
        aves[it.multi_index] = counts[it.multi_index[0], it.multi_index[1], 0]/counts[it.multi_index[0], it.multi_index[1], 1]
        #print counts[it.multi_index[0], it.multi_index[1], 0], counts[it.multi_index[0], it.multi_index[1], 1]
        it.iternext()
    #print counts
    return aves


''' fourier transform 
login_rate = cPickle.load(open('logins_per_hour.pkl', 'rb'))

counts = np.empty(len(login_rate))
dates = np.empty(len(login_rate), dtype=datetime.datetime)

for index, rate in enumerate(login_rate):
    counts[index] = rate['count']
    dates[index] = rate['time']
    
cal = calendar.Calendar()
print np.trim_zeros(np.array(cal.monthdayscalendar(2012,3)).flatten())
print np.trim_zeros(np.array(cal.monthdayscalendar(2012,4)).flatten())

fft_dat = np.fft.fft(counts)
freq = np.fft.fftfreq(counts.size)
max_power = (np.abs(fft_dat)**2.0).max()
total_power = np.sum(np.abs(fft_dat[0:len(counts)/2])**2.0)

mod_freq = freq[len(counts)/2:-1]
power = (np.abs(fft_dat[0:len(counts)/2])**2.0)/total_power

for index, i in enumerate(power):
    print 1.0/freq[index], i
'''

''' frequency magnitude 
login_rate = cPickle.load(open('logins_per_minute.pkl', 'rb'))

counts = np.empty(len(login_rate))
dates = np.empty(len(login_rate), dtype=datetime.datetime)

for index, rate in enumerate(login_rate):
    counts[index] = rate['count']
    dates[index] = rate['time']

cum_freq = {}
total_events = len(counts)

print total_events
for num, count in enumerate(sorted(counts)):
    cum_freq[count] = total_events - (num + 1)

for counts in sorted(cum_freq.iterkeys()):
    print '%f %f'%(float(counts), float(cum_freq[counts])/total_events)
'''

''' permutation entropy 
login_rate = cPickle.load(open('logins_per_hour.pkl', 'rb'))

counts = np.empty(len(login_rate))
dates = np.empty(len(login_rate), dtype=datetime.datetime)

for index, rate in enumerate(login_rate):
    counts[index] = rate['count']
    dates[index] = rate['time']

pe_window = 336
pe_order = 8
results = []
for i in range(pe_window):
    results.append({'h':0, 'date':dates[i], 'counts':counts[i], 'returns_max':0, 'returns_min':0, 'ret_day':0})
    #print '0 %i-%i-%i %f'%(trailing_returns[i][0].year, trailing_returns[i][0].month, trailing_returns[i][0].day, target_data[i])
for i in range(len(counts) - pe_window):
    H = Chaos.permutationEntropy(counts[i:pe_window + i], pe_order)
    results.append({'h':H/math.log(math.factorial(pe_order),2), 'date':dates[pe_window + i], 'counts':counts[pe_window + i], 'returns_max':0, 'returns_min':0, 'ret_day':0})
    #print '%f %i-%i-%i %f'%(H/math.log(math.factorial(pe_order),2), trailing_returns[window + i][0].year, trailing_returns[window + i][0].month, trailing_returns[window + i][0].day, target_data[window + i])
#results_reversed = [i for i in reversed(results)]

for result in results:
    #print '%s %f %i'%(result['date'].strftime("%Y-%m-%dT%H:%M:%S"), result['h'], result['counts'])
    print result['h']
'''

''' output forecast to csv '''
dp = Uber.DemandPredictor()

f = open('uber_demand_prediction_challenge.json','r')
logins = json.loads(f.read())
f.close()

logins_np = np.array([dateutil.parser.parse(x) for x in logins], dtype=datetime.datetime)

for login in logins_np:
    dp.addLogin(login)

f = open('uber_demand_prediction.csv','w')
for single_date in Uber.daterange(datetime.datetime(2012, 5, 1, hour = 0, minute = 0, second = 0), datetime.datetime(2012, 5, 15, hour = 23, minute = 59, second = 59), increment='hours'):
    f.write('%s, %f\n'%(single_date.strftime("%Y-%m-%dT%H:%M:%S"), dp.forecast(single_date.weekday(), single_date.hour)))

f.close()

#for i, count in enumerate(dp.login_counts_test):
#    print count, dp.login_counts[i], dp.day_counts[i]

'''
dp = Uber.DemandPredictor()

f = open('uber_demand_prediction_challenge.json','r')
logins = json.loads(f.read())
f.close()

logins_np = np.array([dateutil.parser.parse(x) for x in logins], dtype=datetime.datetime)

for login in logins_np:
    dp.addLogin(login)

#for count in dp.day_counts:
#    print count

#print dp.forecast(0, 23)
#print dp.login_counts[0, 23], dp.day_counts[0, 23]


days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day = ''
for single_date in daterange(datetime.datetime(2012, 5, 1, hour = 0, minute = 0, second = 0), datetime.datetime(2012, 5, 15, hour = 23, minute = 59, second = 59), increment='hours'):
    if days[single_date.weekday()] == day:
        print '%s, ,%f'%(single_date.strftime("%Y-%m-%dT%H:%M:%S"), dp.forecast(single_date.weekday(), single_date.hour))
    else:
        print '%s, %s, %f'%(single_date.strftime("%Y-%m-%dT%H:%M:%S"), days[single_date.weekday()], dp.forecast(single_date.weekday(), single_date.hour))
        day = days[single_date.weekday()]

#for i, count in enumerate(dp.login_counts_test):
#    print count, dp.login_counts[i], dp.day_counts[i]
'''


''' averages
aves = ave_rate('uber_demand_prediction_challenge.json')

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day = ''
for single_date in daterange(datetime.datetime(2012, 5, 1, hour = 0, minute = 0, second = 0), datetime.datetime(2012, 5, 15, hour = 23, minute = 59, second = 59), increment='hours'):
    if days[single_date.weekday()] == day:
        print '%s, ,%f'%(single_date.strftime("%Y-%m-%dT%H:%M:%S"), aves[single_date.weekday(), single_date.hour])
    else:
        print '%s, %s, %f'%(single_date.strftime("%Y-%m-%dT%H:%M:%S"), days[single_date.weekday()],aves[single_date.weekday(), single_date.hour])
        day = days[single_date.weekday()]
'''
   
''' login rate vs time 
start = datetime.datetime.now()
rate = login_rate('uber_demand_prediction_challenge.json', increment='minutes')
end = datetime.datetime.now()
print end - start


#days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
#day = ''
#for i in rate:
#    if days[i['time'].weekday()] == day:
#        print '%s, ,%i'%(i['time'].strftime("%Y-%m-%dT%H:%M:%S"), i['count'])
#    else:
#        print '%s, %s, %i'%(i['time'].strftime("%Y-%m-%dT%H:%M:%S"), days[i['time'].weekday()], i['count'])
#        day = days[i['time'].weekday()]

cPickle.dump(rate, open('logins_per_minute.pkl', 'wb'))
'''


