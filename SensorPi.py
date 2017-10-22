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
import sys

import LEDManager as LED
from DynamoDBUtility import Table
import BluetoothUtility as BT

#_______________________________________________________________________________

sense = SenseHat()

# Obtain the bluetooth addresses by running `$ hciconfig` in the terminal
gatewayBRAddresses = {
    'B' : 'B8:27:EB:1D:9D:BF'
}

#_______________________________________________________________________________

def collectData(numberOfDataPoints, feature):
    '''
    Param(s):
        (int)   Number of data points to be recorded

    Returns a numpy array that contains humidity, temperature and pressure
    measurements.

    '''

    # Initialize the helper variable
    data_all = np.zeros((numberOfDataPoints, feature + 1))

    for i in range(numberOfDataPoints):
        
        data_all[i][0] = 0
        data_all[i][1] = sense.get_pressure()
        data_all[i][2] = sense.get_temperature_from_humidity()
        data_all[i][3] = sense.get_humidity()

    return data_all

#_______________________________________________________________________________

def main(gatewayLetter, sleepTime):
    '''
    Handles the experiment flow. When ran:
    1)  It listens for a trigger from the 'SampleSize' table on DynamoDB
    2)  Once triggered the Pi collects half the data points specified in the table.
    3)  The Pi then transmits the data to the Gateway Pi via Bluetooth
    4)  The program terminates.

    '''

    table = Table('SampleSize')
    oldSizeTime = 0

    while True:

        # Break out of the inner while-loop only when the table has been updated
        sense.set_pixels(LED.threeDots('green', 'S'))

        stayInLoop = True
        key = {
            'forum'     : '1',
            'subject'   : 'PC1'
        }
        # countTime = 1
        while stayInLoop:
            try:
                stayInLoop, timeStamp = table.compareValues(key, 'timeStamp', oldSizeTime, True)
                # print(countTime, "Old", oldSizeTime, "\tNew", timeStamp)
                time.sleep(sleepTime)
                # countTime += 1

            except KeyboardInterrupt:
                print("Shutting down...")
                sense.set_pixels(LED.pluses('black'))
                sys.exit()

        oldSizeTime = timeStamp

        # Collect the required number of data points
        sense.set_pixels(LED.pluses('green'))

        numberOfDataPoints = int(table.getItem(key)['sampleSize'])
        feature = 3
        startTime = time.time()
        collectedData = collectData(numberOfDataPoints, feature)
        endTime = time.time()
        # print("Sensor :", str(numberOfDataPoints), "data points collected in", str(endTime - startTime), "seconds")

        # Transmit the data via bluetooth to the Gateway Pi
        sense.set_pixels(LED.arrowSend('blue', 'black'))
        btTime = BT.sendDataByBluetooth(collectedData, gatewayLetter, 1)

        # Show that the Pi has completed it's work
        sense.set_pixels(LED.xCross('red'))

#_______________________________________________________________________________

if __name__ == '__main__':
    gatewayLetter = sys.argv[1]     # The letter is used to distinguish tables
    sleepTime = float(sys.argv[2])  # Determines how frequently we'll query the DB
    main(gatewayLetter, sleepTime)
#_______________________________________________________________________________
