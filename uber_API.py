#!/usr/bin/env python
import json
import dateutil.parser
import datetime
import numpy as np
import calendar
import itertools

from flask import Flask, request, Response, render_template, redirect, url_for

import Uber

app = Flask(__name__)

'''
The index page has links to the from_file API and the from_stream API.
'''
@app.route('/')
def index():
    return render_template('index.html', links={'from_file':url_for('from_file', data_file='uber_demand_prediction_challenge.json'), 'from_stream':url_for('from_stream')})

'''
The from_file API. Accepts a get parameter 'data_file' that points at a data file
containing the login data.
'''
@app.route('/from_file', methods=['GET'])
def from_file():
    if request.method == 'GET':
        data_file = request.args.get('data_file', '')
        dp = Uber.DemandPredictor()
        f = open(data_file,'r')
        logins = json.loads(f.read())
        f.close()
        logins_np = np.array([dateutil.parser.parse(x) for x in logins], dtype=datetime.datetime)
        for login in logins_np:
            dp.addLogin(login)
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        forecast = []
        start_date = datetime.datetime(2012, 5, 1, hour = 0, minute = 0, second = 0)
        end_date = datetime.datetime(2012, 5, 15, hour = 23, minute = 59, second = 59)
        current_date = datetime.datetime(1972, 11, 16, hour = 0, minute = 0, second = 0)
        day_index = -1
        for single_date in Uber.daterange(start_date, end_date, increment='hours'):
            if single_date.date() != current_date.date():
                forecast.append(
                    {
                    'display_date': '%s, %s %i'%(days[single_date.weekday()], calendar.month_name[single_date.month], single_date.day),
                    'forecasts': [dp.forecast(single_date.weekday(), single_date.hour)]
                    }
                    )
                current_date = single_date
                day_index += 1
            else:
                forecast[day_index]['forecasts'].append(dp.forecast(single_date.weekday(), single_date.hour));
        return render_template('from_file.html', forecast=json.dumps(forecast))

'''
The from_stream API.
'''
@app.route('/from_stream')
def from_stream():
    dp = Uber.DemandPredictor()
    
    '''
    This is a fake stream of data. It loops over the provided JSON file.
    '''
    def login_stream(logins):
        for login in itertools.cycle(logins):
            parsed_login = dateutil.parser.parse(login)
            dp.addLogin(parsed_login)
            day = parsed_login.weekday()
            hour = parsed_login.hour
            forecast = dp.forecast(day, hour)
            ret = {'day':day, 'hour':hour, 'forecast':forecast}
            yield "data: %s\n\n" % (json.dumps(ret))
    data_file = 'uber_demand_prediction_challenge.json'
    f = open(data_file,'r')
    logins = json.loads(f.read())
    f.close()
    
    if request.headers.get('accept') == 'text/event-stream':
        return Response(login_stream(logins), content_type='text/event-stream')
    return redirect(url_for('static', filename='from_stream.html'))

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
