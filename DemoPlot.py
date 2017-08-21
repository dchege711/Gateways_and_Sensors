'''
Gets data from DynamoDB data and visualizes it using matplotlib.
Make sure you have the table though!

@ Original Author   : Edward Chang
@ Modified by       : Chege Gitau

Note: Still needs debugging.

'''
#_______________________________________________________________________________

import matplotlib.pylab as plt
import math

from DynamoDBUtility import Table

#_______________________________________________________________________________

# Color Codes
lightPurple = '#ddddff'
pink = '#ffb6c1'
paleYellow = '#fdffd0'

# Initialize plot figure to make it accessible by every function
fig, axs = plt.subplots(4,1)
# fig.set_size_inches(20,2)

#_______________________________________________________________________________

def plotBandwidth(resultItem):
    featureBytes = resultItem['data_bytes_features']
    entireDataBytes = resultItem['data_bytes_entire']
    savings = ((entireDataBytes - featureBytes) / entireDataBytes) * 100

    bandwidthCollabel = ['Sensor Data', 'Feature Data', 'Data Savings']
    n = 0
    bandwidthData = [
        [ dp(entireDataBytes, ' bytes', n = n),
          dp(featureBytes, ' bytes', n = n),
          dp(savings, ' %', n = n)
        ]
    ]
    colors = [pink, pink, paleYellow]
    plotTableFigure(0, bandwidthData, bandwidthCollabel, colors, 1, 1.5)


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
        "Data_Latency", "Computation_Latency", "Total_Latency"
    ]

    latency_data = [
        [ "Bluetooth, Wi-Fi", "On-Pi, On-Lambda", "Total Latency"],
        [ dp(bluetoothLatency, 's') + ', ' + dp(awsUploadLatency, 's'),
          dp(piComputationLatency, 's') + ', ' + dp(lambdaComputationLatency, 's'),
          dp(totalLatency, 's')
        ]
    ]

    colors = [pink, pink, paleYellow]
    plotTableFigure(1, latency_data, latency_collabel, colors, 1, 1.5)

#_______________________________________________________________________________

def dp(number, unit, n = 2):
    dp = '{:.' + str(n) + 'f}'
    return dp.format(float(number)) + unit

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
        "AWS DynamoDB", "AWS Lambda", "Total_Cost"
    ]
    dec = 8
    costs_data = [
        [
            "Storage", "Invoke, Compute", "Total"
        ],
        [
            dp(dbCost, '$', n = dec),
            dp(invokeCost, '$', n = dec) + ', ' + dp(computeCost, '$', n = dec),
            dp(totalCost, '$', n = dec)
        ]
    ]
    colors = [pink, pink, paleYellow]
    plotTableFigure(2, costs_data, costs_collabel, colors, 1, 1.5)

#_______________________________________________________________________________

def plotAccuracy(resultItem):
    '''
    Plots a table that shows the observed value, predicted value and error.
    '''
    actualData = resultItem['Real_Result']
    predictedData = resultItem['Prediction']
    predictionError = resultItem['Error']
    accuracy_collabel = ["Observed_Value", "Predicted_Value", "Error"]
    accuracy_data = [
        [actualData, predictedData, predictionError]
    ]
    colors_2 = [pink, pink, paleYellow]
    plotTableFigure(3, accuracy_data, accuracy_collabel, colors_2, 1, 1.5)

#_______________________________________________________________________________

def plotTableFigure(index, cellText, columnLabels, colors, width, height):
    '''
    Helper method for plotting tables using matplotlib

    Param(s):
        (int)   The index of the axis to be used for the table
        (list)  The values that will go into each column
        (list)  The labels that will be used for each column
        (list)  The colors that will be used to denote the columns

    The lists should be of the same length
    '''

    axs[index].axis('tight')
    axs[index].axis('off')
    tableBeingPlotted = axs[index].table(
        cellText    = cellText,
        colLabels   = columnLabels,
        loc         = 'center',
        colColours  = colors
    )

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

    # while True:
    #
    #     # When the results table gets updated, update the figures
    #     resultItem = resultTable.getItem({
    #         'environment'    : 'roomA',
    #         'sensor'         : 'sensorA&B&C'
    #     })
    #
    #     newTime = resultItem['Time']
    #     if oldTime != newTime:
    #         print("Updating tables...")
    #         plotLatency(resultItem)
    #         # plotCosts(resultItem)
    #         # plotAccuracy(resultItem)
    #         oldTime = newTime

#_______________________________________________________________________________

if __name__ == '__main__':
    main()
