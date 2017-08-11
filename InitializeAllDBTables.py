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
initializeTable('Trigger_A', 'forum', 'subject', 'roomA', '1')
initializeTable('SampleSize', 'forum', 'subject', '1', 'PC1')
initializeTable('sensingdata_A', 'forum', 'subject', 'roomA', 'sensorA')
initializeTable('sensingdata_B', 'forum', 'subject', 'roomA', 'sensorB')
initializeTable('sensingdata_C', 'forum', 'subject', 'roomA', 'sensorC')
initializeTable('latency_C', 'forum', 'subject', 'roomA', 'sensorC')
initializeTable('weightresult', 'environment', 'sensor', 'roomA', 'sensorA&B&C')

# Which script sets the values in sensingdata_C and latency_C?

'''
* denotes the key-value pairs that must be included when using the tables
--------------------------------------------------------------------------------
√ TABLE : 'SampleSize'
--------------------------------------------------------------------------------

'forum'         --> (String)*
                        Set by InitializeAllDBTables.py
                        Button.py searches for '1'

'subject'       --> (String)*
                        Set by InitializeAllDBTables.py
                        Button.py searches for 'PC1'

'timeStamp'          -->
                        Set by Button.py
                        Queried by GatewayPi.py to escape loop
                        Queried by SensorPi.py to escape loop

'sampleSize'    -->
                        Set by Button.py
                        Queried by LinearRegressionLambda.py
                        Queried by SensorPi.py
                        Queried by GatewayPi.py

--------------------------------------------------------------------------------
√ TABLE : 'sensingdata_A'   √
--------------------------------------------------------------------------------

'forum'             --> (String)*
                        Set by InitializeAllDBTables.py
                        GatewayPi.py searches for 'roomA'
                        TriggerLambda.py searches for 'roomA'

'subject'           --> (String)*
                        Set by InitializeAllDBTables.py
                        GatewayPi.py searches for 'sensorA'
                        TriggerLambda.py searches for 'sensorA'

'feature_A'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'feature_B'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'feature_C'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Comm_pi_pi'        --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Compu_pi'          --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Comm_pi_lambda'    --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'timeStamp'         --> Set by GatewayPi.py, Queried by TriggerLambda.py

--------------------------------------------------------------------------------
X TABLE : 'sensingdata_B'
--------------------------------------------------------------------------------

'forum'             --> (String)*
                        Set by InitializeAllDBTables.py
                        TriggerLambda.py searches for 'roomA'

'subject'           --> (String)*
                        Set by InitializeAllDBTables.py
                        TriggerLambda.py searches for 'sensorB'

'feature_A'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'feature_B'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'feature_C'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Comm_pi_pi'        --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Compu_pi'          --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Comm_pi_lambda'    --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'timeStamp'         --> Set by GatewayPi.py, Queried by TriggerLambda.py
'data_bytes'        --> Set by GatewayPi.py

--------------------------------------------------------------------------------
√ TABLE : 'sensingdata_C'
--------------------------------------------------------------------------------

'forum'             --> (String)*
                        Set by InitializeAllDBTables.py
                        DemoPlot.py queries for 'roomA'

'subject'           --> (String)*
                        Set by InitializeAllDBTables.py
                        DemoPlot.py queries for '199'

'data_bytes'        --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (how much data has been transmitted)

These keys for the items below are differ in their 'subject' field, e.g.
    ('roomA', '22', 'X_1', 'X_2', ...), ('roomA', '23', 'X_1', 'X_2', ...)

'X_1'               --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (time)
'X_2'               --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (pressure)
'X_3'               --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (humidity)
'Y'                 --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (temperature)


--------------------------------------------------------------------------------
TABLE : 'latency_C'
--------------------------------------------------------------------------------

'forum'             --> (String)*
                        Set by InitializeAllDBTables.py
                        TriggerLambda.py searches for 'roomA'
                        DemoPlot.py queries for 'roomA'

'subject'           --> (String)*
                        Set by InitializeAllDBTables.py
                        TriggerLambda.py searches for 'sensorC'
                        DemoPlot.py queries for 'sensorC'

'Comm_pi_pi'        --> Queried by LinearRegressionLambda.py
'Comm_pi_lambda'    --> Queried by LinearRegressionLambda.py
'ExecTime'          --> Queried by LinearRegressionLambda.py
'timeStamp'         --> Queried by TriggerLambda.py

--------------------------------------------------------------------------------
TABLE : 'weightresult'
--------------------------------------------------------------------------------
'environment'       --> (String)*
                            Set by InitializeAllDBTables.py
                            Set by LinearRegressionLambda.py
                            DemoPlot.py queries for 'roomA'

'sensor'            --> (String)*
                            Set by InitializeAllDBTables.py
                            Set by LinearRegressionLambda.py
                            DemoPlot.py queries for 'sensorA&B&C'

'w_1'               --> Set by LinearRegressionLambda.py
'w_2'               --> Set by LinearRegressionLambda.py
'Prediction'        --> Set by LinearRegressionLambda.py
'Error'             --> Set by LinearRegressionLambda.py
'Lambda_ExecTime'   --> Set by LinearRegressionLambda.py
'Time'              --> Set by LinearRegressionLambda.py, Queried by DemoPlot.py
'Comm_pi_pi'        --> Set by LinearRegressionLambda.py
'Comm_pi_lambda'    --> Set by LinearRegressionLambda.py
'Compu_pi'          --> Set by LinearRegressionLambda.py

--------------------------------------------------------------------------------
TABLE : 'Trigger_A'
--------------------------------------------------------------------------------

'forum'             --> (String)*
                        Set by InitializeAllDBTables.py
                        TriggerLambda.py searches for 'roomA',

'subject'           --> (String)*
                        Set by InitializeAllDBTables.py
                        TriggerLambda.py searches for '1'

'timeStamp'         --> Set by TriggerLambda.py

'''
