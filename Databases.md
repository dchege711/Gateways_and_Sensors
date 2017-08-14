# AWS DynamoDB Tables Documentation
* This is a documentation of the various AWS DynamoDB tables used in the experiment.
* To prepare them (and ensure that you're not missing keys), run InitializeAllDBTables.py for every AWS account that you work in. You only need to do this once for every AWS account.
* '\*' denotes the key-value pairs that must be included when creating, reading, updating and deleting items.

## TABLE : 'SampleSize'
* This table is used mainly as a trigger for the sensors and gateways.
```shell
'forum'         --> (String)*
                        InitializeAllDBTables.py sets a value of 1
                        Button.py searches for 1

'subject'       --> (String)*
                        InitializeAllDBTables.py sets a value of PC1
                        Button.py searches for PC1

'timeStamp'     --> (1, PC1)
                        Button.py sets it to the time when sample size was set.
                        GatewayPi.py escapes loop if cached time does not equal this timeStamp
                        SensorPi.py escapes loop if cached time does not equal this timeStamp

'sampleSize'    --> (1, PC1)
                        Button.py sets it to the number of samples specified.
                        LinearRegressionLambda.py queries it before computation.
                        SensorPi.py queries it before collecting data.
                        GatewayPi.py queries it before listening to data.
```

## TABLE : 'sensingdata_A'
* This table is used to store features calculated by Gateway A.
```shell
'forum'             --> (String)*
                        InitializeAllDBTables.py sets a value of
                        GatewayPi.py searches for 'roomA'
                        TriggerLambda.py searches for 'roomA'

'subject'           --> (String)*
                        InitializeAllDBTables.py sets a value of
                        GatewayPi.py searches for 'sensorA'
                        TriggerLambda.py searches for 'sensorA'

'feature_A'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'feature_B'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'feature_C'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Comm_pi_pi'        --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Compu_pi'          --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Comm_pi_lambda'    --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'timeStamp'         --> Set by GatewayPi.py, Queried by TriggerLambda.py
```

## TABLE : 'sensingdata_B'
* This table is used to store features calculated by Gateway B.
```shell
'forum'             --> (String)*
                        InitializeAllDBTables.py sets a value of
                        TriggerLambda.py searches for 'roomA'

'subject'           --> (String)*
                        InitializeAllDBTables.py sets a value of
                        TriggerLambda.py searches for 'sensorB'

'feature_A'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'feature_B'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'feature_C'         --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Comm_pi_pi'        --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Compu_pi'          --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'Comm_pi_lambda'    --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
'timeStamp'         --> Set by GatewayPi.py, Queried by TriggerLambda.py
'data_bytes'        --> Set by GatewayPi.py
```

## TABLE : 'sensingdata_C'
* This table is used to store the data aggregated from sensor C and gateway C; no features present.
* These keys for the items below are differ in their 'subject' field, e.g.
    `('roomA', '22', 'X_1', 'X_2', ...), ('roomA', '23', 'X_1', 'X_2', ...)`
```shell
'forum'             --> (String)*
                        InitializeAllDBTables.py sets a value of
                        DemoPlot.py queries for 'roomA'

'subject'           --> (String)*
                        InitializeAllDBTables.py sets a value of
                        DemoPlot.py queries for '199'

'data_bytes'        --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py
                        Measure of how much data was uploaded to DynamoDB in bytes.

'X_1'               --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (time)
'X_2'               --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (pressure)
'X_3'               --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (humidity)
'Y'                 --> Set by GatewayPi.py, Queried by LinearRegressionLambda.py (temperature)
```

## TABLE : 'latency_C'
* Honestly, I don't know the function of this table. Stores latency data, but why in a new table?
```shell
'forum'             --> (String)*
                        InitializeAllDBTables.py sets a value of
                        TriggerLambda.py searches for 'roomA'
                        DemoPlot.py queries for 'roomA'

'subject'           --> (String)*
                        InitializeAllDBTables.py sets a value of
                        TriggerLambda.py searches for 'sensorC'
                        DemoPlot.py queries for 'sensorC'

'Comm_pi_pi'        --> Queried by LinearRegressionLambda.py
'Comm_pi_lambda'    --> Queried by LinearRegressionLambda.py
'ExecTime'          --> Queried by LinearRegressionLambda.py
'timeStamp'         --> Queried by TriggerLambda.py
```

## TABLE : 'weightresult'
* Stores the results of the AWS Lambda computations.
```shell
'environment'       --> (String)*
                            InitializeAllDBTables.py sets a value of
                            Set by LinearRegressionLambda.py
                            DemoPlot.py queries for 'roomA'

'sensor'            --> (String)*
                            InitializeAllDBTables.py sets a value of
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
```

## TABLE : 'Trigger_A'
* The AWS Lambda function listens to this table.
* If the table gets updated, the function will start running.
```shell
'forum'             --> (String)*
                        InitializeAllDBTables.py sets a value of
                        TriggerLambda.py searches for 'roomA',

'subject'           --> (String)*
                        InitializeAllDBTables.py sets a value of
                        TriggerLambda.py searches for '1'

'timeStamp'         --> Set by TriggerLambda.py
```
