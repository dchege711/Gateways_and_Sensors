'''
Checks whether the Gateways have finished their transmission.
This is because computational latency may not match transmission latency.

This scripts updates a DynamoDB table that triggers AWS Lambda

@ Original Author   : Edward Chang
@ Modified by       : Chege Gitau

'''
#_______________________________________________________________________________

import time
from DynamoDBUtility import Table

#_______________________________________________________________________________

oldTimeA = 0
oldTimeB = 0
oldTimeC = 0

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
        aIsReady, timeA = tableA.compareValues(oldTimeA, queryA, 'timeStamp', False)
        bIsReady, timeB = tableB.compareValues(oldTimeB, queryB, 'timeStamp', False)
        cIsReady, timeC = tableC.compareValues(oldTimeC, queryC, 'timeStamp', False)

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
			break


    # The Trigger_A table makes Lambda start processing the data.
    # The table needs to be specified in the Lambda function config.
	lambdaTriggerTable = Table('Trigger_A')
	item = lambdaTriggerTable.getItem({
        'forum'     : 'roomA',
        'subject'   : '1'
	})

	tEnd = time.time()
	item['timeStamp'] = tEnd
	lambdaTriggerTable.addItem(item)
