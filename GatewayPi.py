'''
Calculates features from sensor data and transmits this to DB

Gateway 1 and 2 transmit features (hence Computation_Latency)
Gateway 3 transmits the data (hence Transmission Latency)

@ Original Author   : Edward Chang
@ Modified by       : Chege Gitau

'''
#_______________________________________________________________________________

import time
import numpy as np
import sys
from sense_hat import SenseHat
import matplotlib.pylab as plt
from decimal import Decimal

import LEDManager as LED
from DynamoDBUtility import Table
import BluetoothUtility as BT
sense = SenseHat()

#_______________________________________________________________________________

# Different Gateways perform different operations
# Some Gateways aggregate data, calculate features and transmit only the features to DynamoDB.
# Some Gateways aggregate data and send all this data to DynamoDB
calculateFeatures = {
'A' : True,
'B' : True,
'C' : False
}

#_______________________________________________________________________________

def bluetoothDataToNPArrays(dataFromBT, numDataPoints, numFeatures):
    '''
    Transcribes the data received via bluetooth to numpy arrays.

    Param(s):
    (num)
    '''

    designMatrix = np.zeros((numDataPoints * 2, numFeatures))
    targetMatrix = np.zeros((numDataPoints * 2, 1))

    for i in range(numDataPoints):
        designMatrix[i][0] = dataFromBT[i][0] / 10000000
        designMatrix[i][1:numFeatures] = dataFromBT[i][1:numFeatures]
        targetMatrix[i][0] = dataFromBT[i][numFeatures]

    return targetMatrix, designMatrix

#_______________________________________________________________________________

def collectData(targetMatrix, designMatrix, numDataPoints):
    '''
    Collects data required by the Gateway Pi
    Appends this data to that received from bluetooth

    Param(s):
        (int)   Number of data points to be collected
    '''

    for i in range(numDataPoints):

        tdataTime = time.time()
        designMatrix[i + numDataPoints][0] = tdataTime/10000000
        designMatrix[i + numDataPoints][1] = sense.get_pressure()
        designMatrix[i + numDataPoints][2] = sense.get_humidity()
        targetMatrix[i + numDataPoints][0] = sense.get_temperature_from_humidity()

    return targetMatrix, designMatrix

#_______________________________________________________________________________

def gradientDescent(targetMatrix, designMatrix, numFeatures, numDataPoints):
    '''
    Runs the gradient descent algorithm.

    Param(s):
        (numpy array)   The target matrix
        (numpy array)   The design matrix

    Returns a numpy array of features that approximate the mapping
    '''

    count = 0
    w_old = np.zeros((numFeatures, 1))
    w_new = np.zeros((numFeatures, 1))
    E_old = 0
    E_new = 0
    delta_E = np.zeros((numDataPoints * 2, numFeatures))
    learning_rate = 0.001

    while True:
        w_old = w_new

        for i in range(numDataPoints * 2):

            delta_E[i,:] = delta_E[i,:] + (targetMatrix[i][0] - np.dot(np.matrix(designMatrix[i,:]),np.matrix(w_old)))*designMatrix[i,:]

        w_new = w_old + learning_rate * np.matrix(delta_E[i, :] / (numDataPoints * 2)).T
        E_old = E_new

        for i in range(numDataPoints * 2):
            E_new = E_new + (targetMatrix[i][0] - np.dot(np.matrix(designMatrix[i, :]), np.matrix(w_new))) ** 2
            E_new = E_new / 2

        if E_new > E_old:
            learning_rate = learning_rate / 2

        count = count + 1
        print("E_new", E_new, "E_old", E_old)

        # I'm running into an infinite loop at this point
        # if E_new == E_old:
        if E_new < E_old:
            break

    return w_new

#_______________________________________________________________________________

def uploadToDB(tableLetter, data, btTime, compTime):
    '''
    Uploads the features and the latencies to DynamoDB

    Param(s):
        (char)          Denotes the table, e.g. A, B
        (numpy array)   Features calculated from the dataset
        (int)           Time taken to load bluetooth data in seconds
        (int)           Time taken to compute the features in seconds

    Returns an int showing the time taken to upload to DynamoDB in seconds

    '''

    startTime = time.time()
    table = Table('sensingdata_' + tableLetter)
    room = 'roomA'
    sensor = 'sensor' + tableLetter

    # Prepare the upload payload
    item = table.getItem({
        'forum'     : room,
        'subject'   : sensor
    })

    # If the Gateway was designated to calculate features...
    if calculateFeatures[tableLetter]:
        item['feature_A'] = Decimal(str(float(data[0][0])))
        item['feature_B'] = Decimal(str(float(data[1][0])))
        item['feature_C'] = Decimal(str(float(data[2][0])))
        sizeOfDataInBytes = data.nbytes

    # Otherwise, the Gateway was meant to aggregate data without calculations
    else:
        designMatrix = data[0]
        targetMatrix = data[1]

        # Numpy indexes follow the [row][column] convention
        # ndarray.shape returns the dimensions as a (#OfRows, #OfColumns)
        # Both of our matrices have the same number of rows, hence one measure is enough
        numOfRows = designMatrix.shape[0]
        aggregatedItems = []

        for i in numOfRows:
            item = {}
            item['X_1']     = Decimal(str(designMatrix[i][0]))    # Time
            item['X_2']     = Decimal(str(designMatrix[i][1]))    # Pressure
            item['X_3']     = Decimal(str(designMatrix[i][2]))    # Humidity
            item['Y']       = Decimal(str(targetMatrix[i][0]))    # Temperature
            aggregatedItems.append(item)

        sizeOfDataInBytes = designMatrix.nbytes + targetMatrix.nbytes
        item['aggregated_data'] = Decimal(str(aggregatedItems))

    # Upload this document to DynamoDB
    item['Comm_pi_pi'] = Decimal(str(btTime))
    item['Compu_pi'] = Decimal(str(compTime))
    item['data_bytes'] = Decimal(str(sizeOfDataInBytes))
    table.addItem(item)

    # Attach a time stamp and the size of the file to the header item in DynamoDB
    endTime = time.time()
    uploadDuration = endTime - startTime
    item['Comm_pi_lambda'] = Decimal(str(uploadDuration))
    item['timeStamp'] = Decimal(str(endTime))
    table.addItem(item)

    return uploadDuration

#_______________________________________________________________________________

def visualizeData(btTime, compTime, uploadTime):
    '''
    Sets up a non-blocking visualization of the experiment's results.
    '''

    plt.close()
    fig, axs = plt.subplots(1,1)
    fig.set_size_inches(2,2)
    clust_data = [[[btTime],'10','15']]
    collabel = [
        "Bluetooth Transmission Time (sec)",
        "Data Collection Time (sec)",
        "ML Computation Time (sec)"
    ]
    axs.axis('tight')
    axs.axis('off')
    tableFigure = axs.table(
        cellText    = clust_data,
        colLabels   = collabel,
        loc         ='center'
    )

    tableFigure.scale(1.3,1.5)
    plt.show(block=False)

#_______________________________________________________________________________

def main(tableLetter):
    '''
    Runs the experiment as indicated below:

    1)  Listens for a trigger on the 'SampleSize' table on DynamoDB
    2)  On the trigger, starts listening and reading from bluetooth (port 1)
    3)  Collects additional data from its sensors
    4)  Calculates the features of the data
    5)  Uploads the features to DynamoDB
    6)  Visualizes these results using an animated matplotlib figure.

    '''

    oldSizeTime = 0 # Placeholder. The value will be overwritten by a time stamp

    while True:

        # Establish a connection to the 'SampleSize' table
        table = Table('SampleSize')

        # Break out of the inner while-loop only when the table has been updated
        sense.set_pixels(LED.threeDots('green'))

        stayInLoop = True
        key = {
        'forum'     : '1',
        'subject'   : 'PC1'
        }

        while stayInLoop:
            stayInLoop, timeStamp = table.compareValues(key, 'timeStamp', oldSizeTime, True)
            # Sleep for 10 seconds because pinging AWS is costly
            time.sleep(10)
        oldSizeTime = timeStamp

        numDataPoints = int(table.getItem(key)['sampleSize'])
        numFeatures = 3

        # Listen for incoming bluetooth data on port 1
        sense.set_pixels(LED.arrow('orange'))

        timeOne = time.time()
        dataFromBT = BT.listenOnBluetooth(1)
        timeTwo = time.time()

        # Signify the computation state
        sense.set_pixels(LED.diamond('blue'))

        # Transform the received bluetooth data to numpy arrays
        targetMatrix, designMatrix = bluetoothDataToNPArrays(dataFromBT, numDataPoints, numFeatures)

        # Aggregate the bluetooth data, with data collected from the Gateway Pi
        sense.set_pixels(LED.pluses('green'))
        targetMatrix, designMatrix = collectData(targetMatrix, designMatrix, numDataPoints)

        # Signify the computation state
        sense.set_pixels(LED.diamond('blue'))

        # Calculate the features if the gateway has permission to do so
        if calculateFeatures[tableLetter]:
            features = gradientDescent(targetMatrix, designMatrix, numFeatures, numDataPoints)

        timeThree = time.time()
        btTime = timeTwo - timeOne
        compTime = timeThree - timeTwo

        # Upload data to DynamoDB
        sense.set_pixels(LED.arrow('blue'))

        if calculateFeatures[tableLetter]:
            uploadTime = uploadToDB(tableLetter, features, btTime, compTime)

        else:
            uploadTime = uploadToDB(tableLetter, [targetMatrix, designMatrix], btTime)

        # Reset the state of the LED
        sense.set_pixels(LED.xCross('red'))

        # Visualize the results
        visualizeData(btTime, compTime, uploadTime)

#_______________________________________________________________________________

if __name__ == '__main__':
    tableLetter = sys.argv[1]   # The letter is used to distinguish tables
    main(tableLetter)
