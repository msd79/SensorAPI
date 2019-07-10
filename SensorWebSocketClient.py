from socketIO_client import SocketIO
import requests
import json

def call_back():
    print('call_back_received')
try:
    with SocketIO('192.168.0.103', 5000, wait_for_connection=False) as socketIO:
        socketIO.emit('insidetemp_broadcast_event', {'data': '22.000', }, call_back)
        socketIO.emit('outsidetemp_broadcast_event', {'data': '05.000', }, call_back)
        socketIO.wait_for_callbacks(seconds=1)
except:
    print("Unable to connnect")

url = "http://api.openweathermap.org/data/2.5/weather?lat=53.235721&lon=-1.4586242&units=metric&APPID=c8562d06892415b442aef4ac9315fbc5"
response = requests.get(url) # push the json data to the API
myjson = response.content.decode("utf-8").replace("'", '"')
json.loads(myjson)
print(json.loads(myjson)["main"]["temp"])
json.loads(myjson)["main"]["temp_max"]
json.loads(myjson)["main"]["temp_min"]
json.loads(myjson)["main"]["humidity"]
#print(dir(response.json))

#json.loads(myjson)
#{'base': 'stations', 'clouds': {'all': 40}, 'main': {'temp_max': 7, 'pressure': 990, 'temp': 6, 'temp_min': 5, 'humidity': 87}, 'wind': {'deg': 210, 'speed': 8.7}, 'id': 2653225, 'coord': {'lon': -1.42, 'lat': 53.25}, 'name': 'Chesterfield', 'dt': 1513165800, 'cod': 200, 'visibility': 10000, 'sys': {'id': 5062, 'message': 0.0053, 'sunset': 1513180043, 'type': 1, 'country': 'GB', 'sunrise': 1513152772}, 'weather': [{'icon': '10d', 'id': 500, 'main': 'Rain', 'description': 'light rain'}]}


