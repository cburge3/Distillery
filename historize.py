from __future__ import print_function
from time import strftime, localtime, sleep
from os import fsync
import paho.mqtt.client as mqttClient
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

history_interval = 10
mqtt_hub_ip = '192.168.1.9'

scope = 'io/IOC1/in/#'
logfile = open("databases\\tempdata" + strftime("%a_%d_%b_%H_%M_%S", localtime()) + ".log", 'w')

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe('scope')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # assume that unique tag is last in the MQTT topic structure
    topic = msg.topic
    payload = msg.payload.decode()
    print(msg.topic+" "+msg.payload.decode())
    timestamp = strftime("%a %d %b %Y %H:%M:%S", localtime())
    logfile.write(','.join([timestamp, topic, payload]) + '\n')
    # make sure to push the python and windows buffers to the file in case of ungraceful exit
    logfile.flush()
    fsync(logfile.fileno())

def setup_historian():
    client = mqttClient.Client()
    client.username_pw_set('ionodes', '1jg?8jJ+Ut8,')
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(mqtt_hub_ip, 1883, 60)
    print("Connecting engine to MQTT server...")
    client.loop_start()


if __name__ == '__main__':
    # client = mqttClient.Client()
    # client.username_pw_set('ionodes', '1jg?8jJ+Ut8,')
    # client.on_connect = on_connect
    # client.on_message = on_message
    # client.connect(mqtt_hub_ip, 1883, 60)
    # print("Connecting engine to MQTT server...")
    # client.loop_forever()
    """
    Shows basic usage of the Sheets API. Prints values from a Google Spreadsheet.
    """

    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('databases\\client-secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    RANGE_NAME = 'Class Data!A2:E'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                 range=RANGE_NAME).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[4]))

