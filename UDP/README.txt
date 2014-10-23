Uber Coding Challenge Solution

Michael Sachs

Included files:
* README.txt - This file.
* uber_demand_prediction_challenge.json - The provided data.
* UDP_description.pdf - A description of my prediction approach and a couple 
                        of different approaches to analyzing the data.
* UDP.csv - The predictions in CSV format.
* Uber.py - The DemandPredictor class and utility functions.
* uber_CSV.py - Used to generate the UDP.csv file.
* uber_API.py - The two Flask APIs.
* templates/index.html - For displaying the APIs
* templates/from_file.html - For displaying the APIs
* static/from_stream.html - For displaying the APIs
* static/css/uber.css - For displaying the APIs
* static/fonts/* - For displaying the APIs

uber_CSV.py usage:
Just run 'python uber_CSV.py' from the command line. This will read the 
'uber_demand_prediction_challenge.json' file and output predictions
in 'UDP.csv'.

uber_API.py usage:
With Flask installed, run 'python uber_API.py' from the command line. Flask 
runs a development server and will print out the local URL for this server.
In a browser (I only tested under Safari 6.0.5 and Google Chrome 28.0.1500.71
on MacOS 10.8.4) navigate to this URL. Links to the streaming and file loading
APIs will be at the root URL.