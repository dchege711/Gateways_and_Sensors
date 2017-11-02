'''
Checks whether the Gateways have finished their transmission.
This is because computational latency may not match transmission latency.

This scripts updates a DynamoDB table that triggers AWS Lambda

@ Original Author   : Edward Chang
@ Modified by       : Chege Gitau

'''
#_______________________________________________________________________________

import time
import sys
from DynamoDBUtility import Table
from decimal import Decimal
import matplotlib.pylab as plt
import DemoPlot as dp
from collections import namedtuple

from lambda_utility import aws_lambda
import accuracy_test
lambda_client = aws_lambda()

#_______________________________________________________________________________

# Initialize helper variables for plotting the table
# Color Codes
lightPurple = '#ddddff'
pink = '#ffb6c1'
paleYellow = '#fdffd0'

# Initialize plot figure to make it accessible by every function
fig, axs = plt.subplots(4, 1)
#plt.ion() # Makes the plot interactive
#plt.show()

def trigger_using_dynamodb():
    # The Trigger_A table makes Lambda start processing the data.
    # The table needs to be specified in the Lambda function config.
    lambdaTriggerTable = Table('Trigger_A')
    item = lambdaTriggerTable.getItem({
    'forum'     : 'roomA',
    'subject'   : 'PC1'
    })

    tEnd = time.time()
    item['timeStamp'] = Decimal(str(tEnd))
    lambdaTriggerTable.addItem(item)
    print("Lambda triggered!")
    print()

def trigger_using_lambda_client():
    startTime = time.time()
    response = lambda_client.invoke("LinearRegressionLambda")
    endTime = time.time()
    # print(response)
    # print()
    # print("Time taken on AWS Lambda :", str(endTime-startTime), "seconds.")
    # print()

    return response

def tabulate_cloud_vs_fog(resultItem):

    cloud_results = populate_values(resultItem["all_cloud"])
    fog_results = populate_values(resultItem["fog (edge + cloud)"])

    colors = [pink, paleYellow]

    column_labels = ["Experiment ID", "Experiment ID"]
    id_one = " ".join([
        str(cloud_results.readings_per_sensor), 
        "readings per sensor, for", str(cloud_results.number_of_sensors), "sensors" 
    ])
    id_two = " ".join([
        str(fog_results.readings_per_sensor), 
        "readings per sensor, for", str(fog_results.number_of_sensors), "sensors" 
    ])
    cell_values = [[id_one, id_two]]
    # plot_table_figure(0, cell_values, column_labels, colors)

    column_labels = ["Cost (Cloud)", "Cost (Fog)"]
    cell_values = [[str(cloud_results.total_cost) + " $", str(fog_results.total_cost) + " $"]]
    # plot_table_figure(1, cell_values, column_labels, colors)

    column_labels = ["Latency (Cloud)", "Latency (Fog)"]
    cell_values = [[str(cloud_results.total_latency) + " sec", str(fog_results.total_latency) + " sec"]]
    # plot_table_figure(2, cell_values, column_labels, colors)

    column_labels = ["Mean Square Error (Cloud)", "Mean Square Error (Fog)"]
    cell_values = [[cloud_results.error, fog_results.error]]
    # plot_table_figure(3, cell_values, column_labels, colors)

    # return cell_values_a, cell_values_b, cell_values_c, cell_values_d
    
def populate_values(data):

    total_latency = data["Comm_pi_pi"] + data["Comm_pi_lambda"] + data["Compu_pi"] + data["Lambda_ExecTime"]

    if data["fog_or_cloud"] == "all_cloud":
        type_of_run = "All Cloud"
        data_bytes_sent = data["data_bytes_entire"] * 3
    else:
        type_of_run = "Fog (Edge + Cloud)"
        data_bytes_sent = data["data_bytes_entire"] + data["data_bytes_features"] * 2

    total_cost = 0
    costs = dp.estimate_costs(data_bytes_sent, data["Lambda_ExecTime"])
    for cost in costs:
        total_cost += cost

    error = data["Error"]
    readings_per_sensor = data["readings_per_sensor"]
    number_of_sensors = data["number_of_sensors"]

    summary = namedtuple('summary', 
        [
            'total_cost', 'total_latency', 'type_of_run',
            'error', 'readings_per_sensor', 'number_of_sensors'
    ])

    results = summary(
        total_cost, total_latency, type_of_run,
        error, readings_per_sensor, number_of_sensors
    )

    return results

def plot_table_figure(index, cellText, columnLabels, colors):

    width = 1.0
    height = 1.65
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


def print_results(results):
    results = populate_values(results)
    header = " ".join([
        "\nResults for", str(results.readings_per_sensor), 
        "readings per sensor for the", results.type_of_run, "setup...\n"
    ])
    print(header)
    print("Estimated Cost \t\t:", results.total_cost)
    print("Estimated Latency \t:", results.total_latency)
    print("Estimated Error\t\t:", results.error)

oldTimeA, oldTimeB, oldTimeC = 0, 0, 0

queryA = {
    'forum'     : 'roomA',
    'subject'   : 'sensorA'
}
queryB = {
    'forum'     : 'roomA',
    'subject'   : 'sensorB'
}
queryC = {
    'forum'     : 'roomA',
    'subject'   : 'sensorC'
}

tableA = Table('sensingdata_A')
tableB = Table('sensingdata_B')
tableC = Table('sensingdata_C')


# Uncomment this block to check whether you're getting desired results
for result in accuracy_test.get_all_results():
    print_results(result)

while True:

    ready = 0

    # This while-loop is only escaped once all the Gateway Pi's are done
    while True:

        try:
            # Challenge: If GatewayPi.py is using the same document as the 
            # one being requested by TriggerLambda, the document will be unavailable
            # The KeyError doesn't mean that the key doesn't really exist
            try:
                aIsReady, timeA = tableA.compareValues(queryA, 'timeStamp', oldTimeA, False)
            except KeyError:
                pass   

            try:
                bIsReady, timeB = tableB.compareValues(queryB, 'timeStamp', oldTimeB, False)
            except KeyError:
                pass   

            try:
                cIsReady, timeC = tableC.compareValues(queryC, 'timeStamp', oldTimeC, False)
            except KeyError:
                pass

            if aIsReady:
                ready = ready + 1
                oldTimeA = timeA
            if bIsReady:
                ready = ready + 1
                oldTimeB = timeB
            if cIsReady:
                ready = ready + 1
                oldTimeC = timeC

            # This means that all gateways are ready
            if ready >= 3:
                ready = 0
                print("Now triggering lambda...")
                print()
                break

        except KeyboardInterrupt:
            print("Closing Lambda Trigger")
            print()
            sys.exit()

    # trigger_using_dynamodb()
    results = trigger_using_lambda_client()


