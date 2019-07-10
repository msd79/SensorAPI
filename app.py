#from threading import Lock
from flask import Flask, jsonify, abort, request, render_template, session
from flask_socketio import SocketIO, emit
import pymysql
import dbAccess
import json

#async_mode = None

app=Flask(__name__)
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
#thread = None
#thread_lock = Lock()

import ptvsd
try:
    ptvsd.enable_attach(secret='qwerty', address = ('192.168.0.103', 3000))
    #ptvsd.wait_for_attach()
    #ptvsd.break_into_debugger()
except:
    pass


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/sensor/temp', methods=['GET'])
def readTemp():
  """REST GET method for the purpose  of retriving sensor data"""
  db = dbAccess.DB(pymysql) # Instantiate DB class and pass pymysql module to be used
  rows = db.select("Select * from ambienttemp") # Run select query against DB
  collection = [] #Initiate an empty list
  #print(rows)
  for row in rows:  # For each row of records returned from the DB
        
        reading = {  # Create a dictionary object 
        'timestamp' : row[0],
        'data' : row[1],
        'comment' : row[2]     
      }
        collection.append(reading) # append the dictionay object to the list

  return jsonify({'reading': collection}),201 # Jsonify the list and return as response along with the HTTP code 201(Created)


@app.route('/api/sensor/temp', methods=['POST'])
def pushTempReading():
    """REST POST method for the purpose  of pushing sensor data""" 
    if not request.json or not 'data' in request.json: # If request received by the API is not a json or it doesnt contain a 'data' entry
        abort(400) #return HTTP code 400 (Bad request)
    reading = { # Create a dictionay object using the data in the request.json as values
        'timestamp' : request.json["timestamp"],
        'data' : request.json["data"],
        'comment' : request.json["comment"]
        }
    db = dbAccess.DB(pymysql) # Instantiate DB class and pass pymysql module to be used
    query =  db.generateQueryString(reading["timestamp"], reading["data"], reading["comment"])# Genereate a query string
    result = db.insert(query) # Pass the query to insert method of the DB class 
    print(query)
    return jsonify({'reading': reading}),201


@socketio.on('my_event')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data']})

@socketio.on('insidetemp_broadcast_event')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('inside_temp',
         {'data': message['data'], 'count': session['receive_count']},
broadcast=True)

@socketio.on('outsidetemp_broadcast_event')
def test_broadcast_message(message):
    emit('outside_temp',
         {'data': message['data']},
broadcast=True)

if __name__ == '__main__':
      #app.run(debug=True, host='0.0.0.0')
      socketio.run(app, host='0.0.0.0')
      
      
