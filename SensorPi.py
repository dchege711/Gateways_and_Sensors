'''
Collects temperature, pressure and humidity data and pushes it to the
Gateway Pi via Bluetooth.

@ Original Author   : Edward Chang
@ Modified by       : Chege Gitau

'''
#_______________________________________________________________________________

import bluetooth
import os
import cPickle
import numpy as np
from sense_hat import SenseHat
import time

import LEDManager as LED
from DynamoDBUtility import Table

#_______________________________________________________________________________

sense = SenseHat()

#_______________________________________________________________________________

def sendDataByBluetooth(data, bd_addr, port):
    '''
    Param(s):
        (String)    Destination Address
        (int)       Destination Port

    Sends data over bluetooth to the designated address and port.
    Run "$ hciconfig dev" on the Pi to identify the address

    '''
    # Communicate status to the outside world
    sense.set_pixels(LED.arrow)
    # Establish the bluetooth connection
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((bd_addr, port))
    # Send the data
    startTime = time.time()
    sock.send(cPickle.dumps(data))
    endTime = time.time()
    sock.close()
    # Communicate status to the outside world
    sense.set_pixels(LED.xCross)
    print("Sensor : Sent data over bluetooth in", str(endTime - startTime), "seconds")

#_______________________________________________________________________________

def collectData(numberOfDataPoints, feature):
    '''
    Param(s):
        (int)   Number of data points to be recorded

    Returns a numpy array that contains humidity, temperature and pressure
    measurements.

    '''
    # Communicate status via the LED lights
    sense.set_pixels(LED.diamond)
    # Initialize the helper variable
    data_all = np.zeros((datanum, feature + 1))

    for i in range(numberOfDataPoints):
        # Record several parameters of interest
        device = {}
        device['cpuTemperature'] = os.popen('vcgencmd measure_temp').readline().replace("temp=","").replace("'C\n","")

        temp = {}
        temp['basedOnHumidity'] = sense.get_temperature_from_humidity()
        temp['basedOnPressure'] = sense.get_temperature_from_pressure()

        environment = {}
        environment['humidity'] = sense.get_humidity()
        environment['pressure'] = sense.get_pressure()
        environment['temperature'] = temp

        message = {}
        message['device'] = device
        message['environment'] = environment

        tdataTime = time.time()

        data_all[i][0] = tdataTime
        data_all[i][1] = sense.get_pressure()
        data_all[i][2] = sense.get_humidity()
        data_all[i][3] = sense.get_temperature_from_humidity()

    return data_all

#_______________________________________________________________________________

def main():
    '''
    Handles the experiment flow. When ran:
    1)  It listens for a trigger from the 'SampleSize' table on DynamoDB
    2)  Once triggered the Pi collects half the data points specified in the table.
            LED Pattern = Diamond
    3)  The Pi then transmits the data to the Gateway Pi via Bluetooth
            LED Pattern = Arrow
    4)  The program terminates.
            LED Pattern = Cross

    '''

    table = Table('SampleSize')
    old_size_time = 0

    while True:

        # Break out of the inner while-loop only when the table has been updated
        stayInLoop = True
        key = {
            'forum'     : '1',
            'subject'   : 'PC1'
        }
        while stayInLoop:
            stayInLoop, timeStamp = table.compareValues(key, 'timeStamp', oldSizeTime, True)
        oldSizeTime = timeStamp

        # Collect the required number of data points
        numberOfDataPoints = int(table.getItem(key)['SampleSize'])
        feature = 3
        startTime = time.time()
        collectedData = collectData(numberOfDataPoints, feature)
        endTime = time.time()
        print("Sensor :", str(numberOfDataPoints), "data points collected in", str(endTime - startTime), "seconds")

        # Transmit the data via bluetooth to the Gateway Pi
        sendDataByBluetooth(collectedData, "XX:XX:EB:57:29:XX", 1)

#_______________________________________________________________________________

if __name__ == '__main__':
    # main()
    get = 9
#_______________________________________________________________________________
