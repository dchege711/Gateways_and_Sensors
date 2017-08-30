'''
Initializes all the tables that will be used by the experiment

@ Original Author   : Chege Gitau

'''
#_______________________________________________________________________________

from DynamoDBUtility import Table

#_______________________________________________________________________________

def initializeTable(nameOfTable, hashKey, rangeKey, hashVal, rangeVal):
    '''
    Helper method for initializing tables. Assumes all inputs are strings

    Param(s):
        (String)   Name of the table being created
        (String)   Name of the hash key. Assumed to be AWS type 'S'
        (String)   Name of the range key. Assumed to be AWS type 'S'
        (String)   Value of the hash key for the first item
        (String)   Value of the range key for the first item

    '''
    table = Table(nameOfTable, [hashKey, 'S'], [rangeKey, 'S'])
    table.addItem({
        hashKey    : hashVal,
        rangeKey   : rangeVal
    })

#_______________________________________________________________________________

# Initialize all the required tables
initializeTable('SampleSize', 'forum', 'subject', '1', 'PC1')
initializeTable('sensingdata_A', 'forum', 'subject', 'roomA', 'sensorA')
initializeTable('sensingdata_B', 'forum', 'subject', 'roomA', 'sensorB')
initializeTable('sensingdata_C', 'forum', 'subject', 'roomA', 'sensorC')
initializeTable('weightresult', 'environment', 'sensor', 'roomA', 'sensorA&B&C')
initializeTable('Trigger_A', 'forum', 'subject', 'roomA', '1')
