# import lots of libraries
from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time
import os
import glob
from picamera import PiCamera
import Adafruit_DHT
import Adafruit_ADS1x15

# camera setup
camera = PiCamera()

# DHT setup
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 17

# Air Quality setup
adc = Adafruit_ADS1x15.ADS1115()
BaseENV = 760  # obtained by running the sensor in normal condiitons for 10 minutes
GAIN = 1

now_time = datetime.now()
current_time = str(now_time.strftime("%Y/%m/%d %H:%M"))
pic_name = now_time.strftime("%Y_%m_%d_%H_%M")

# My Spreadsheet ID
MY_SPREADSHEET_ID = '18sofK-We-G_dYruqnfuBxhfDc9zCZSfAzR3qm0_b6nE'


def update_sheet(sheetname, temperature, humidity, AirQuality):
    # authentication, authorization step
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'creds.json', SCOPES)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API, append the next row of sensor data
    # values is the array of rows we are updating, its a single row
    values = [[current_time,
               temperature, humidity, AirQuality]]
    body = {'values': values}
    # call the append API to perform the operation
    result = service.spreadsheets().values().append(
        spreadsheetId=MY_SPREADSHEET_ID,
        range='Sheet1!A1:B1',
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=body).execute()


# temperature reading code

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'  # finding the serial number of the temp sensor
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def snap():
    camera.capture('/home/pi/SIOTproj/MushPictures/{}.jpg'.format(pic_name))

def hum():
    humidity, bad_temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    return humidity

def PPMDetect():
    PPMCount = []
    for i in range(5):
        values = [0]
        values = adc.read_adc(0, gain=GAIN)
        PPMCount.append(values)
        time.sleep(0.5)
    AveragePPMReading = sum(PPMCount) / 5
    AirQuality = (1 - (AveragePPMReading - BaseENV) / 200) * 100
    return AirQuality


def main():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        humidity = hum()
        AirQuality = PPMDetect()
        print(temp_c, humidity, AirQuality)
        update_sheet("Logger", round(temp_c, 2), round(humidity, 2), round(AirQuality, 2))
        snap()

if __name__ == '__main__':
    main()
