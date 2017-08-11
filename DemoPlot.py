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
lightPurple = '#DDDDFF'
pink = 'FFD0DF'
paleYellow = '#FDFFD0'

# Initialize plot figure to make it accessible by every function
fig, axs =plt.subplots(3,1)
fig.set_size_inches(20,2)

#_______________________________________________________________________________

def plotLatency(resultItem):
    '''
    Plots a table that shows the amount of data sent, and the latencies for
    Bluetooth data transfer, DynamoDB upload, AWS Lambda Computation, and
    Raspberry Pi Computation.

    '''

    latencyCTable = Table('latency_C')
    latencyCItem = latencyCTable.getItem({
        'forum'   : 'roomA',
        'subject' : 'sensorC'
    })

	bluetoothLatency = resultItem['bluetoothLatency']
	awsUploadLatency = resultItem['awsUploadLatency']
	piComputationLatency = resultItem['piComputationLatency']
	lambdaComputationLatency = resultItem['Lambda_ExecTime']
	totalLatency = bluetoothLatency + awsUploadLatency + piComputationLatency + lambdaComputationLatency
	dataSizeInBytes = latencyCItem['data_bytes']

	latency_collabel= [
        "Data_Amount", "Communication_Latency", "Communication_Latency",
        "Computation_Latency", "Computation_Latency", "Total_Latency"
    ]
	latency_data = [
        [
            "(Bytes)", "Sensor_Pi -> Gateway_Pi", "Gateway_Pi -> Lambda",
            "Gateway_Pi", "Lambda", "(seconds)"
        ],
		[
            dataSizeInBytes, bluetoothLatency, awsUploadLatency,
            piComputationLatency, lambdaComputationLatency, totalLatency
        ]
    ]

	colors = ['gray', lightPurple, lightPurple, pink, pink, paleYellow]

	axs[0].axis('tight')
	axs[0].axis('off')
	the_table_latency = axs[0].table(
        cellText    = latency_data,
        colLabels   = latency_collabel,
        loc         = 'center',
        colColours  = colors
    )
	the_table_latency.scale(1.3,1.5)

#_______________________________________________________________________________

def plotCosts(resultItem):
    '''
    Plots a table that shows the cost of storing the data on DynamoDB, invoking
    AWS Lambda and computing on AWS Lambda

    '''
    # Get the cost of storing data on AWS Lambda
	dbGBHourRate = 0.25
	dynamoDBCost = dataSizeInBytes * (dbGBHourRate / (1024 * 1024))

    # Get the cost of invoking AWS Lambda
	numLambdaInvocations = 1
	lambdaInvokeCostPerReq = 0.0000002
	lambdaInvokeTotalCost = numLambdaInvocations * lambdaInvokeCostPerReq

    # Get the cost of computing on AWS Lambda
    lambdaComputeCostPerSec = 0.000000208
	lambdaComputeTime = resultItem['ExecTime']
	lambdaComputeTime = math.ceil(float(lambdaComputeTime * 10))
	lambdaComputeTotalCost = (lambdaComputeTime / 10) * lambdaComputeCostPerSec

    # Plot the cost data
	totalCost = dynamoDBCost + lambdaInvokeTotalCost + lambdaComputeTotalCost
	costs_collabel= [
        "DynamoDB_Storage", "Lambda_Invocation", "Lambda_Computation", "Total_Cost"
    ]
	costs_data = [
        [
            "dynamoDBCost", "lambdaInvokeTotalCost",
            "lambdaComputeTotalCost", "(USD)"
        ],
		[
            dynamoDBCost, lambdaInvokeTotalCost,
            lambdaComputeTotalCost, totalCost
        ]
    ]
	colors = [lightPurple, pink, pink, paleYellow]
    plotTableFigure(1, costs_data, costs_collabel, colors)

#_______________________________________________________________________________

def plotAccuracy(resultItem):
    '''
    Plots a table that shows the observed value, predicted value and error.
    '''
    sensingCTtable = Table('sensingdata_C')
    sensingCItem = sensingCTtable.getItem({}
        'forum'   : 'roomA',
        'subject' : '199'
    })

	actualData = sensingCItem['Y']
	predictedData = resultItem['Prediction']
	predictionError = resultItem['Error']
	accuracy_collabel = ["Observed_Values", "Predicted_Values", "Error"]
	accuracy_data = [
        [actualData, predictedData, predictionError]
    ]
    colors_2 = [lightPurple, pink, paleYellow]
	plotTableFigure(2, accuracy_data, accuracy_collabel, colors_2)

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

    axs[index].axis('tight')
    axs[index].axis('off')
    tableBeingPlotted = axs[2].table(
        cellText    = cellText,
        colLabels   = columnLabels,
        loc         = 'center',
        colColours  = colors
    )

    tableBeingPlotted.scale(1.3,1.5)

#_______________________________________________________________________________

def main():
    
    oldTime = 0

    while True:

        # When the results table gets updated, escape this loop
        resultTable = Table('weightresult')
    	while True:
    		resultItem = resultTable.getItem({
    			'environment'    : 'roomA',
    			'sensor'         : 'sensorA&B&C'
    	    })
    		if oldTime != resultItem['Time']:
    			oldTime = resultItem['Time']
    			break
    		else:
    			oldTime = resultItem['Time']
        plotLatency(resultItem)
        plotCosts(resultItem)
        plotAccuracy(resultItem)
        plt.show(block=False)

#_______________________________________________________________________________

if __name__ == '__main__':
    main()
