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
import sys
import numpy as np
from decimal import Decimal

from DynamoDBUtility import Table

#_______________________________________________________________________________

# Color Codes
lightPurple = '#ddddff'
pink = '#ffb6c1'
paleYellow = '#fdffd0'

# Initialize plot figure to make it accessible by every function
# I nullified this to prevent extra figures when importing this file
fig, axs = None, None
# The line below was moved to the if __name__ == "__main__" block
# fig, axs = plt.subplots(5-int(sys.argv[1]), 1)

#_______________________________________________________________________________

def compareAllCloudVsFog(resultItem):
    resultTable = Table('weightresult')
    allCloudStats = makeLists(resultTable, 'all_cloud_results')
    fogStats = makeLists(resultTable, 'expResults')
    # print(fogStats)

    # Plot comparisons
    pyplot.figure(1)
    pyplot.rcParams.update({'figure.figsize': [0.6, 1.4]})
    pyplot.rcParams.update({'font.size': 22})

    # pyplot.grid(True)
    pyplot.xlabel("Number of Readings", fontsize = 25)
    pyplot.ylabel("Time Spent in Computation (sec)", fontsize = 25)
    pyplot.title("Comparing All-Cloud Computation to Fog Computation")

    pyplot.scatter(allCloudStats[0], allCloudStats[1], color = 'r', label = "All-Cloud")
    pyplot.scatter(fogStats[0], fogStats[1], color = 'b', label = "Fog")

    pyplot.legend(loc = 'best')

    # Plot comparisons
    pyplot.figure(2)
    pyplot.rcParams.update({'figure.figsize': [0.6, 1.4]})
    pyplot.rcParams.update({'font.size': 22})

    # pyplot.grid(True)
    pyplot.xlabel("Number of Readings", fontsize = 25)
    pyplot.ylabel("Total Time from Reading to Prediction", fontsize = 25)
    pyplot.title("Comparing All-Cloud Latency to Fog Latency")

    pyplot.scatter(allCloudStats[0], allCloudStats[2], color = 'r', label = "All-Cloud")
    pyplot.scatter(fogStats[0], fogStats[2], color = 'b', label = "Fog")
    
    pyplot.legend(loc = 'best')
    

def makeLists(resultTable, sensorValue):

    overallStats = resultTable.getItem({
        'environment'   : 'roomA',
        'sensor'        : sensorValue
    })['results']

    summarizedStats = {}

    # print(sensorValue, "\n")

    for stat in overallStats:
        # Each reading is 32 bytes and each gateway submits two sets of readings
        # Update variable names: We now have total number of readings
        numReadingsPerSensor = (stat['data_bytes_entire'] / (32 * 2))
        computationLatency = stat['Compu_pi'] + stat['Lambda_ExecTime']
        totalLatency = stat['Comm_pi_pi'] + stat['Comm_pi_lambda'] + computationLatency
        # print(numReadingsPerSensor, stat['Comm_pi_lambda'], computationLatency, totalLatency)

        if numReadingsPerSensor not in summarizedStats.keys():
            summarizedStats[numReadingsPerSensor] = [computationLatency, totalLatency]

        # print(summarizedStats[numReadingsPerSensor][0], computationLatency)
        # if summarizedStats[numReadingsPerSensor][0] > computationLatency:
        #     summarizedStats[numReadingsPerSensor][0] = computationLatency
        #     # print("Replaced Stats Compu")

        # if summarizedStats[numReadingsPerSensor][1] > totalLatency:
        #     summarizedStats[numReadingsPerSensor] = totalLatency
        #     # print("Replaced Stats Total")

    # for key in summarizedStats:
    #     print(key, ":", summarizedStats[key])
    
    readingsPerSensorList = []
    compuLatencyList = []
    totalLatencyList = []
    for reading in summarizedStats.keys():
        readingsPerSensorList.append(reading)
        compuLatencyList.append(summarizedStats[reading][0])
        totalLatencyList.append(summarizedStats[reading][1])

    # print(readingsPerSensorList)
    # print("\n")
    # print(compuLatencyList)
    # print("\n")
    # print(totalLatencyList)
    # print("\n")
    return readingsPerSensorList, compuLatencyList, totalLatencyList


def plotBandwidth(resultItem):
    featureBytes = resultItem['data_bytes_features']
    entireDataBytes = resultItem['data_bytes_entire']
    numSensors = resultItem['number_of_sensors']

    # Because the gateway reports data for 2 sensors
    intendedBytes = entireDataBytes * numSensors / 2
    sentBytes = entireDataBytes + featureBytes

    reduction = 100 - ((sentBytes / intendedBytes) * 100)

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
        "Communication Latency", "Computation Latency", "Total Latency"
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

def estimate_costs(data_bytes_entire, lambda_exec_time):
    dbGBHourRate = 0.25
    dataSizeInBytes = float(data_bytes_entire)
    dbCost = dataSizeInBytes * (dbGBHourRate / (1024 * 1024))

    # Get the cost of invoking AWS Lambda
    numLambdaInvocations = 1
    lambdaInvokeCostPerReq = 0.0000002
    invokeCost = numLambdaInvocations * lambdaInvokeCostPerReq

    # Get the cost of computing on AWS Lambda
    lambdaComputeCostPerSec = 0.000000208
    lambdaComputeTime = lambda_exec_time
    lambdaComputeTime = math.ceil(float(lambdaComputeTime * 10))
    computeCost = (lambdaComputeTime / 10) * lambdaComputeCostPerSec

    return dbCost, invokeCost, computeCost


def plotCosts(resultItem):
    '''
    Plots a table that shows the cost of storing the data on DynamoDB, invoking
    AWS Lambda and computing on AWS Lambda

    '''
    dbCost, invokeCost, computeCost = estimate_costs(
        resultItem['data_bytes_entire'],
        resultItem['Lambda_ExecTime']
    )

    # Plot the cost data
    totalCost = dbCost + invokeCost + computeCost
    costs_collabel= [
        "AWS DynamoDB", "AWS Lambda", "Total Cost"
    ]
    dec = 2
    lambdaCost = dp(invokeCost, '\$', n = dec, targetType = 'e') + ', ' + dp(computeCost, '\$', n = dec, targetType = 'e')
    costs_data = [
        [
            "Storage", "Invocation, Computation", "Total Cost"
        ],
        [
            dp(dbCost, '$', n = dec),
            # dp(lambdaCost, '$', n = dec, targetType = 'e'),
            lambdaCost,
            dp(totalCost, '$', n = dec)
        ]
    ]
    colors = [pink, pink, paleYellow]
    plotTableFigure(2, costs_data, costs_collabel, colors)

#_______________________________________________________________________________

def plotAccuracy(resultItem, figureNumber):
    '''
    Plots a graph that shows the observed values, predicted values and error.
    '''
    predictedData = resultItem['Prediction']
    realData = resultItem['Real_Data']

    xUnits = list(range(len(predictedData)))
    error = '{:.4f}'.format(resultItem['Error'])

    pyplot.figure(int(figureNumber))
    pyplot.rcParams.update({'figure.figsize': [0.6, 1.4]})
    pyplot.rcParams.update({'font.size': 22})

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
    width = 1.0
    height = 1.65
    # height = len(cellText) * 0.7
    # print("Height :", height)
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
    figureNumber = sys.argv[1]
    oldTime = 0
    resultTable = Table('weightresult')
    resultItem = resultTable.getItem({
        'environment'    : 'roomA',
        'sensor'         : 'sensorA&B&C'
    })
    plotBandwidth(resultItem)
    plotLatency(resultItem)
    plotCosts(resultItem)
    plotAccuracy(resultItem, figureNumber)
    # compareAllCloudVsFog(resultItem)
    plt.show()

#_______________________________________________________________________________

if __name__ == '__main__':
    fig, axs = plt.subplots(5-int(sys.argv[1]), 1)
    main()
