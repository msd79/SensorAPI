#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  9 21:42:56 2017

@author: Jonathan Bertram & Serhat Damlica
"""
import ptvsd
import json
import requests
from socketIO_client import SocketIO
try:
    ptvsd.enable_attach(secret='qwerty', address = ('192.168.0.100', 3000))
    #ptvsd.wait_for_attach()
    #ptvsd.break_into_debugger()
except:
    pass

class AmbientTemp(json.JSONEncoder): # Create AmbientTemp class to hold the temp data
    def __init__(self, timestamp, data, comment=""): # Set class constructor
        self.timestamp = timestamp  # Initlize class members with the data passed in to constructor
        self.data = data
        self.comment = comment
    def __str__(self):
        return self.timestamp+','+ self.data +','+ self.comment

def hexAsString(value):
    '''
    function to convert the bytearray value returned
    from the sensor using pygatt to a string of hex values
    for use in the conversion funcion, convertToCel
    '''
    from binascii import hexlify
    
    hexValue = hexlify(value)
    strValue = str(hexValue, 'utf-8')
    strTemp = strValue[0:2]+" "+ strValue[2:4] +" "+ strValue[4:6] +" "+ strValue[6:8]
    return strTemp

def convertToCel(reading):
    '''
    function to convert temperature in hex form to Celcius
    '''
    raw_temp_data = reading # Start with raw data from SensorTag
    raw_temp_bytes = raw_temp_data.split() # Split into individual bytes
    raw_ambient_temp = int( '0x'+ raw_temp_bytes[3]+ raw_temp_bytes[2], 16) # Choose ambient temperature (reverse bytes for little endian)
    ambient_temp_int = raw_ambient_temp >> 2 & 0x3FFF # Shift right, based on from TI
    ambient_temp_celsius = float(ambient_temp_int) * 0.03125 # Convert to Celsius based on info from TI
    ambient_temp_fahrenheit = (ambient_temp_celsius * 1.8) + 32 # Convert to Fahrenheit
    return ambient_temp_celsius

#Callback function for the socket emit
def call_back():
    print('call_back_received')

def socket_client(functiontoCall, msg, callbackFunction):
    try:
        with SocketIO('192.168.0.103', 5000, wait_for_connection=False) as socketIO:
            socketIO.emit(functiontoCall, {'data':  msg, }, callbackFunction)
            socketIO.wait_for_callbacks(seconds=1)
    except:
         print("Unable to connnect to the Socket IO Hub")

#main program
import pygatt
import time
adapter = pygatt.GATTToolBackend()
finish = False
while finish == False:
    try:
        adapter.start() # Start the adapter
        device = adapter.connect('54:6C:0E:53:13:29') # Connect to the SensortTag
        print('Recording temperatures...........')
        print('\nPress Ctrl C to stop')
        device.char_write_handle(0x27, [0x01]) # Enable temprature sensor on the SensorTag
        
        while True:
            try:
                time.sleep(30)
                readTime = time.strftime('%d-%m-%y %H:%M:%S', time.localtime()) #get current time
                print(readTime)
                value = device.char_read_handle('0x24') #get temperature data from the sensor, type bytearray
                strTemp = hexAsString(value) #convert to string of hex values
                insideTemp = convertToCel(strTemp) #convert to celcius

                reading = AmbientTemp(readTime,insideTemp,'comment from the agent' ) # Create an instance of the class
                jsondump = json.dumps(reading.__dict__)# Produce JSON from the class object

                url = "http://localhost:5000/api/sensor/temp"
                response = requests.post(url, data=jsondump,headers={"Content-Type": "application/json" }) # push the json data to the API
                print(response) # Print response returned from the API

                #Make a call to Open Weather Map and request the weather infromation for the coordinates lat=53.235721&lon=-1.4586242 which is Manor Offices
                url = "http://api.openweathermap.org/data/2.5/weather?lat=53.235721&lon=-1.4586242&units=metric&APPID=c8562d06892415b442aef4ac9315fbc5"
                weathermapResponse = requests.get(url) # push the json data to the API
                jsonDecode = weathermapResponse.content.decode("utf-8").replace("'", '"')
                outsideTemp =  json.loads(jsonDecode)["main"]["temp"]
                #json.loads(jsonFormat)
                #{'base': 'stations', 'clouds': {'all': 40}, 'main': {'temp_max': 7, 'pressure': 990, 'temp': 6, 'temp_min': 5, 'humidity': 87}, 'wind': {'deg': 210, 'speed': 8.7}, 'id': 2653225, 'coord': {'lon': -1.42, 'lat': 53.25}, 'name': 'Chesterfield', 'dt': 1513165800, 'cod': 200, 'visibility': 10000, 'sys': {'id': 5062, 'message': 0.0053, 'sunset': 1513180043, 'type': 1, 'country': 'GB', 'sunrise': 1513152772}, 'weather': [{'icon': '10d', 'id': 500, 'main': 'Rain', 'description': 'light rain'}]}
                
                #Call Socket IO Hub functions to push the data to the HTML page
                socket_client('insidetemp_broadcast_event', insideTemp, call_back)
                socket_client('outsidetemp_broadcast_event', outsideTemp, call_back)
                #socket_client(reading)
                # try:
                #     with SocketIO('192.168.0.103', 5000, wait_for_connection=False) as socketIO:
                #         socketIO.emit('insidetemp_broadcast_event', {'data': celcius, }, call_back)
                #         socketIO.emit('outsidetemp_broadcast_event', {'data': outsideTemp, }, call_back)
                #         socketIO.wait_for_callbacks(seconds=1)
                # except:
                #     print("Unable to connnect to socket HUB")


            except KeyboardInterrupt:
                print('\nStopping recording & exiting')
                adapter.stop() # Stop the adapter and disconnect from the sensor
                finish = True # Set the flag to stop the while loop
                break
    except pygatt.exceptions.NotConnectedError:   
        response = input("Unable to connect.\n\nCheck the sensor is switched on then press 'Return' to try again: ")
        if response != '':
            break
