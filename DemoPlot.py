'''
Gets data from DynamoDB data and visualizes it using matplotlib.
Make sure you have the table though!

@ Original Author   : Edward Chang
@ Modified by       : Chege Gitau

Note: Still needs debugging.

'''
#_______________________________________________________________________________

import matplotlib.pylab as plt
import matplotlib.pyplot as pyplot
import math
import numpy as np
from matplotlib.pylab import rcParams

from DynamoDBUtility import Table

#_______________________________________________________________________________

# Color Codes
lightPurple = '#ddddff'
pink = '#ffb6c1'
paleYellow = '#fdffd0'

# Initialize plot figure to make it accessible by every function
fig, axs = plt.subplots(3, 1)
fig.set_figwidth(0.6)

#_______________________________________________________________________________

def plotBandwidth(resultItem):
    featureBytes = resultItem['data_bytes_features']
    entireDataBytes = resultItem['data_bytes_entire']
    numSensors = resultItem['number_of_sensors']

    # Because the gateway reports data for 2 sensors
    intendedBytes = entireDataBytes * numSensors / 2
    sentBytes = entireDataBytes + featureBytes

    reduction = (sentBytes / intendedBytes) * 100

    bandwidthCollabel = ['Sensed Data', 'Sent Data', 'Data Reduction']
    bandwidthData = [
        [ dp(intendedBytes, 'bytes', n = 0),
          dp(sentBytes, 'bytes', n = 0),
          dp(reduction, '%', n = 2)
        ]
    ]
    colors = [pink, pink, paleYellow]
    plotTableFigure(0, bandwidthData, bandwidthCollabel, colors)


def plotLatency(resultItem):
    '''
    Plots a table that shows the amount of data sent, and the latencies for
    Bluetooth data transfer, DynamoDB upload, AWS Lambda Computation, and
    Raspberry Pi Computation.

    '''

    bluetoothLatency = resultItem['Comm_pi_pi']
    awsUploadLatency = resultItem['Comm_pi_lambda']
    piComputationLatency = resultItem['Compu_pi']
    lambdaComputationLatency = resultItem['Lambda_ExecTime']

    totalLatency = bluetoothLatency + awsUploadLatency + piComputationLatency + lambdaComputationLatency

    # dataLatency = str(bluetoothLatency, awsUploadLatency)
    latency_collabel= [
        "Data Latency", "Computation Latency", "Total Latency"
    ]

    latency_data = [
        [ "Bluetooth, Wi-Fi", "Pi, Lambda", "Total Latency"],
        [ dp(bluetoothLatency, 's') + ', ' + dp(awsUploadLatency, 's'),
          dp(piComputationLatency, 's') + ', ' + dp(lambdaComputationLatency, 's'),
          dp(totalLatency, 's')
        ]
    ]

    colors = [pink, pink, paleYellow]
    plotTableFigure(1, latency_data, latency_collabel, colors)

#_______________________________________________________________________________

def dp(number, unit, targetType = 'f', n = 2, suffix = True):
    dp = ''.join(['{:,.', str(n), targetType, '}'])
    if suffix:
        return ' '.join([dp.format(float(number)), unit])
    return ' '.join([unit, dp.format(float(number))])

#_______________________________________________________________________________

def plotCosts(resultItem):
    '''
    Plots a table that shows the cost of storing the data on DynamoDB, invoking
    AWS Lambda and computing on AWS Lambda

    '''
    # Get the cost of storing data on AWS Lambda
    dbGBHourRate = 0.25
    dataSizeInBytes = float(resultItem['data_bytes_entire'])
    dbCost = dataSizeInBytes * (dbGBHourRate / (1024 * 1024))

    # Get the cost of invoking AWS Lambda
    numLambdaInvocations = 1
    lambdaInvokeCostPerReq = 0.0000002
    invokeCost = numLambdaInvocations * lambdaInvokeCostPerReq

    # Get the cost of computing on AWS Lambda
    lambdaComputeCostPerSec = 0.000000208
    lambdaComputeTime = resultItem['Lambda_ExecTime']
    lambdaComputeTime = math.ceil(float(lambdaComputeTime * 10))
    computeCost = (lambdaComputeTime / 10) * lambdaComputeCostPerSec

    # Plot the cost data
    totalCost = dbCost + invokeCost + computeCost
    costs_collabel= [
        "AWS DynamoDB", "AWS Lambda", "Total Cost"
    ]
    dec = 2
    costs_data = [
        [
            "Storage", "Invocation, Computation", "Total"
        ],
        [
            dp(dbCost, '$', n = dec, suffix = False),
            (
                dp(invokeCost, '$', n = dec, targetType = 'e', suffix = False)
                + ', ' + dp(computeCost, '$', n = dec, targetType = 'e', suffix = False)
            ),
            dp(totalCost, '$', n = dec, suffix = False)
        ]
    ]
    colors = [pink, pink, paleYellow]
    plotTableFigure(2, costs_data, costs_collabel, colors)

#_______________________________________________________________________________

def plotAccuracy(resultItem):
    '''
    Plots a graph that shows the observed values, predicted values and error.
    '''
    predictedData = resultItem['Prediction']
    realData = resultItem['Real_Data']

    xUnits = list(range(len(predictedData)))
    error = '{:.4f}'.format(resultItem['Error'])

    pyplot.figure()
    pyplot.rcParams.update({'font.size': 25})

    # pyplot.grid(True)
    pyplot.xlabel("Samples", fontsize = 25)
    pyplot.ylabel("Temperature", fontsize = 25)
    pyplot.title("Comparing Observed Temperature to Predicted Temperature")

    pyplot.plot(xUnits, realData, color = 'r', label = "Real Data")
    pyplot.plot(xUnits, predictedData, color = 'b', label = "Predicted Data")
    # Coordinates are of the form x, y scaled according to the current figure
    xSpot = xUnits[-1] - 300
    ySpot = realData[0]
    pyplot.text(xSpot, ySpot, r'$\Delta = $' + error, bbox = dict(facecolor='blue', alpha=0.5))
    pyplot.legend(loc = 'best')

#_______________________________________________________________________________

def plotTableFigure(index, cellText, columnLabels, colors):
    '''
    Helper method for plotting tables using matplotlib

    Param(s):
        (int)   The index of the axis to be used for the table
        (list)  The values that will go into each column
        (list)  The labels that will be used for each column
        (list)  The colors that will be used to denote the columns

    The lists should be of the same length
    '''
    width = 0.6
    height = 2.0
    axs[index].axis('tight')
    axs[index].axis('off')
    tableBeingPlotted = axs[index].table(
        cellText    = cellText,
        colLabels   = columnLabels,
        loc         = 'center',
        colColours  = colors
    )

    tableBeingPlotted.auto_set_font_size(False)
    tableBeingPlotted.set_fontsize(20)
    tableBeingPlotted.scale(width, height)

#_______________________________________________________________________________

def main():

    oldTime = 0
    resultTable = Table('weightresult')
    resultItem = resultTable.getItem({
        'environment'    : 'roomA',
        'sensor'         : 'sensorA&B&C'
    })
    plotBandwidth(resultItem)
    plotLatency(resultItem)
    plotCosts(resultItem)
    plotAccuracy(resultItem)
    plt.show()

#_______________________________________________________________________________

if __name__ == '__main__':
    main()
