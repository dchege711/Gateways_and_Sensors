"""
Calculates features from sensor data and transmits this to DB

Gateway A and B transmit features (hence Computation_Latency)
Gateway C transmits the data (hence Transmission Latency)

@ Original Author   : Edward Chang
@ Modified by       : Chege Gitau

"""
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
import Button
sense = SenseHat()

#_______________________________________________________________________________

# Different Gateways perform different operations
# Some Gateways aggregate data, calculate features and transmit only the features to DynamoDB.
# Some Gateways aggregate data and send all this data to DynamoDB
# In the all_cloud branch, every gateway acts as a relay instead of a computing edge.

fog_configuration = {
    'A' : True,
    'B' : True,
    'C' : False
}

cloud_configuration = {
    'A' : False,
    'B' : False,
    'C' : False
}

#_______________________________________________________________________________

def bluetoothDataToNPArrays(dataFromBT, numDataPoints, numFeatures):
    """
    Transcribes the data received via bluetooth to numpy arrays.

    Param(s):

    """

    designMatrix = np.zeros((numDataPoints * 2, numFeatures))
    targetMatrix = np.zeros((numDataPoints * 2, 1))

    for i in range(numDataPoints):
        designMatrix[i][0] = dataFromBT[i][0] / 10000000
        designMatrix[i][1:numFeatures] = dataFromBT[i][1:numFeatures]
        targetMatrix[i][0] = dataFromBT[i][numFeatures]

    return targetMatrix, designMatrix

#_______________________________________________________________________________

def collectData(targetMatrix, designMatrix, numDataPoints):
    """
    Collects data required by the Gateway Pi
    Appends this data to that received from bluetooth

    Param(s):
        (int)   Number of data points to be collected
    """

    for i in range(numDataPoints):

        designMatrix[i + numDataPoints][0] = 150.811042787
        designMatrix[i + numDataPoints][1] = sense.get_pressure()
        designMatrix[i + numDataPoints][2] = sense.get_humidity()
        targetMatrix[i + numDataPoints][0] = sense.get_temperature_from_humidity()

    return targetMatrix, designMatrix

#_______________________________________________________________________________

def gradientDescent(targetMatrix, designMatrix, numFeatures, numDataPoints):
    """
    Runs the gradient descent algorithm.

    Param(s):
        (numpy array)   The target matrix
        (numpy array)   The design matrix

    Returns a numpy array of features that approximate the mapping
    """

    count = 0
    w_old = np.zeros((numFeatures, 1))
    w_new = np.zeros((numFeatures, 1))
    E_old = 0
    E_new = 0
    delta_E = np.zeros((numDataPoints * 2, numFeatures))
    learning_rate = 0.001
    # tolerance = 1e-5

    while True:
        w_old = w_new

        for i in range(numDataPoints * 2):
            delta_E[i,:] = delta_E[i,:] + (targetMatrix[i][0] - np.dot(np.matrix(designMatrix[i,:]), np.matrix(w_old))) * designMatrix[i,:]

        w_new = w_old + learning_rate * np.matrix(delta_E[i, :] / (numDataPoints * 2)).T
        E_old = E_new

        for i in range(numDataPoints * 2):
            E_new = E_new + (targetMatrix[i][0] - np.dot(np.matrix(designMatrix[i, :]), np.matrix(w_new))) ** 2
            E_new = E_new / 2

        if E_new > E_old:
            learning_rate = learning_rate / 2

        count = count + 1
        if count % 20 == 0:
            print(str(count), " iterations so far...")
            print()

        # Comparing E_new == E_old is tricky because of precision.
        if np.isclose(E_new, E_old)[0]:
            print("Escaped loop after", str(count), "iterations.")
            print()
            break

    return w_new

#_______________________________________________________________________________

def uploadToDB(tableLetter, data, btTime, compTime, numSensors, calculateFeatures):
    """
    Uploads the features and the latencies to DynamoDB

    Param(s):
        (char)          Denotes the table, e.g. A, B
        (numpy array)   Features calculated from the dataset
        (int)           Time taken to load bluetooth data in seconds
        (int)           Time taken to compute the features in seconds

    Returns an int showing the time taken to upload to DynamoDB in seconds

    """

    startTime = time.time()
    table = Table('sensingdata_' + tableLetter)
    room = 'roomA'
    sensor = 'sensor' + tableLetter

    # Prepare the upload payload (overwrite the previous entry)
    item = {}
    item['forum'] = room
    item['subject'] = sensor
    aggregatedItems = []

    # If the Gateway was designated to calculate features...
    if calculateFeatures[tableLetter]:
        item['feature_A'] = Decimal(str(float(data[0][0])))
        item['feature_B'] = Decimal(str(float(data[1][0])))
        item['feature_C'] = Decimal(str(float(data[2][0])))
        sizeOfDataInBytes = data.nbytes

    # Otherwise, the Gateway was meant to aggregate data without calculations
    else:
        targetMatrix = data[0]
        designMatrix = data[1]

        # Numpy indexes follow the [row][column] convention
        # ndarray.shape returns the dimensions as a (#OfRows, #OfColumns)
        # Both of our matrices have the same number of rows, hence one measure is enough
        numOfRows = designMatrix.shape[0]

        for i in range(numOfRows):
            currentItem = {}
            currentItem['X_1']     = Decimal(str(designMatrix[i][0]))    # Time
            currentItem['X_2']     = Decimal(str(designMatrix[i][1]))    # Pressure
            currentItem['X_3']     = Decimal(str(designMatrix[i][2]))    # Humidity
            currentItem['Y']       = Decimal(str(targetMatrix[i][0]))    # Temperature
            aggregatedItems.append(currentItem)

        sizeOfDataInBytes = designMatrix.nbytes + targetMatrix.nbytes
        item['aggregated_data'] = aggregatedItems

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
    item['number_of_sensors'] = Decimal(str(numSensors))
    table.addItem(item)

    # Log the experiment run to DynamoDB, regardless of gateway type
    item.pop('aggregated_data', None)
    item.pop('forum', None)
    item.pop('subject', None)
    # newData = []
    # labels = []
    # for key in item.keys():
    #     labels.append(key)
    #     newData.append(item[key])

    record = table.getItem({'forum' : 'roomA', 'subject' : 'records'})
    try:
        data = record['data']
    except KeyError:
        record['data'] = []
    data.append(item)
    # record['data_labels'] = labels

    table.addItem(record)

    print("Uploaded ", str(sizeOfDataInBytes), " bytes of data to DynamoDB")
    print()

    # Keep a log of the data indexed by the timestamp
    # The time stamp can then be used to get match up corresponding data.
    loggingItem = {}
    loggingItem['forum'] = room
    loggingItem['subject'] = str(endTime)
    loggingItem['aggregated_data'] = aggregatedItems
    table.addItem(loggingItem)

    return uploadDuration

#_______________________________________________________________________________

def visualizeData(btTime, compTime, uploadTime):
    """
    Sets up a non-blocking visualization of the experiment's results.
    """

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

def main(tableLetter, sleepTime, calculateFeatures):
    """
    Runs the experiment as indicated below:

    1)  Listens for a trigger on the 'SampleSize' table on DynamoDB
    2)  On the trigger, starts listening and reading from bluetooth (port 1)
    3)  Collects additional data from its sensors
    4)  Calculates the features of the data
    5)  Uploads the features to DynamoDB
    6)  Visualizes these results using an animated matplotlib figure.

    """
    # Establish a connection to the 'SampleSize' table
    table = Table('SampleSize')
    oldSizeTime = 0 # Placeholder. The value will be overwritten by a time stamp
    t_stamp_for_last_fog = 0

    while True:

        # Break out of the inner while-loop only when the table has been updated
        sense.set_pixels(LED.threeDots('green', 'G'))

        stayInLoop = True
        key = {
            'forum'     : '1',
            'subject'   : 'PC1'
        }

        while stayInLoop:
            try:
                stayInLoop, timeStamp = table.compareValues(key, 'timeStamp', oldSizeTime, True)
                # Sleep for 10 seconds because pinging AWS is costly
                time.sleep(sleepTime)

            except KeyboardInterrupt:
                print("Shutting down...")
                print()
                sense.set_pixels(LED.pluses('black'))
                sys.exit()

        oldSizeTime = timeStamp

        numDataPoints = int(table.getItem(key)['sampleSize'])

        if numDataPoints == -1:
            sense.set_pixels(LED.pluses('black'))
            sys.exit()

        numFeatures = 3

        # Listen for incoming bluetooth data on port 1
        sense.set_pixels(LED.arrowReceive('orange', 'black'))

        timeOne = time.time()
        btTime, dataFromBT = BT.listenOnBluetooth(1)
        timeTwo = time.time()
        # Edit: timeTwo - timeOne != btTime since some time is spent waiting on the sockets

        # Signify the computation state
        sense.set_pixels(LED.diamond('blue'))

        # Transform the received bluetooth data to numpy arrays
        targetMatrix, designMatrix = bluetoothDataToNPArrays(dataFromBT, numDataPoints, numFeatures)

        # Aggregate the bluetooth data, with data collected from the Gateway Pi
        sense.set_pixels(LED.pluses('green'))
        targetMatrix, designMatrix = collectData(targetMatrix, designMatrix, numDataPoints)

        # Signify the computation state
        sense.set_pixels(LED.diamond('blue'))

        # Calculate how many sensors were used.
        # Number of received readings divided by the number of readings per sensor.
        numSensors = targetMatrix.shape[0] / numDataPoints

        # Calculate the features if the gateway has permission to do so
        if calculateFeatures[tableLetter]:
            features = gradientDescent(targetMatrix, designMatrix, numFeatures, numDataPoints)

        timeThree = time.time()
        # btTime = timeTwo - timeOne
        compTime = timeThree - timeTwo

        # Upload data to DynamoDB
        sense.set_pixels(LED.arrowSend('blue', 'black'))

        if calculateFeatures[tableLetter]:
            uploadTime = uploadToDB(tableLetter, features, btTime, compTime, numSensors, calculateFeatures)

        else:
            # Make sure that targetMatrix and designMatrix get read in the correct order
            uploadTime = uploadToDB(tableLetter, [targetMatrix, designMatrix], btTime, compTime, numSensors, calculateFeatures)

        # Reset the state of the LED
        sense.set_pixels(LED.xCross('red'))

        if t_stamp_for_last_fog != oldSizeTime:
            # Run a fog implementation for a quick comparison
            calculateFeatures = fog_configuration 
            t_stamp_for_last_fog = Button.sample_size(sample_size=numDataPoints)

        else:
            calculateFeatures = cloud_configuration


#_______________________________________________________________________________

if __name__ == '__main__':
    tableLetter = sys.argv[1]       # The letter is used to distinguish tables
    sleepTime = float(sys.argv[2])  # Determines how frequently we'll query the DB

    main(tableLetter, sleepTime, cloud_configuration)
