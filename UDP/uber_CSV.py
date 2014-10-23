import dateutil.parser
import datetime
import json
import numpy as np

import Uber

''' output forecast to csv '''
dp = Uber.DemandPredictor()

f = open('uber_demand_prediction_challenge.json','r')
logins = json.loads(f.read())
f.close()

logins_np = np.array([dateutil.parser.parse(x) for x in logins], dtype=datetime.datetime)

for login in logins_np:
    dp.addLogin(login)

f = open('UDP.csv','w')
for single_date in Uber.daterange(datetime.datetime(2012, 5, 1, hour = 0, minute = 0, second = 0), datetime.datetime(2012, 5, 15, hour = 23, minute = 59, second = 59), increment='hours'):
    f.write('%s, %f\n'%(single_date.strftime("%Y-%m-%dT%H:%M:%S"), dp.forecast(single_date.weekday(), single_date.hour)))

f.close()