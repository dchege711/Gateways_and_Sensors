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

from lambda_utility import aws_lambda
lambda_client = aws_lambda()

#_______________________________________________________________________________

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
    for key in response.keys():
        print(key, "\t:", response[key])
    print()
    print("Time taken on AWS Lambda :", str(endTime-startTime), "seconds.")
    print()


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
tableC = Table('sensingdata_C') # I changed this since I don't see latency_C's purpose

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
    trigger_using_lambda_client()