# AWS DynamoDB Tables Documentation
* This is a documentation of the various AWS DynamoDB tables used in the experiment.
* To prepare them (and ensure that you're not missing keys), run InitializeAllDBTables.py for every AWS account that you work in. You only need to do this once for every AWS account.
* '\*' denotes the key-value pairs that must be included when creating, reading, updating and deleting items.

## TABLE : 'SampleSize'
* This table is used mainly as a trigger for the sensors and gateways.
```
'forum'         --> (String)*
                        InitializeAllDBTables.py sets a value of '1'
                        Button.py searches for '1'

'subject'       --> (String)*
                        InitializeAllDBTables.py sets a value of 'PC1'
                        Button.py searches for 'PC1'

'timeStamp'     --> ('1', 'PC1')
                        Button.py sets it to the time when sample size was set.
                        GatewayPi.py escapes loop if cached time does not equal this timeStamp
                        SensorPi.py escapes loop if cached time does not equal this timeStamp

'sampleSize'    --> ('1', 'PC1')
                        Button.py sets it to the number of samples specified.
                        LinearRegressionLambda.py queries it before computation.
                        SensorPi.py queries it before collecting data.
                        GatewayPi.py queries it before listening to data.
```

* The tables whose name is of the form sensingdata_<letter> have similar forms.
* In GatewayPi.py, there's this block of code:
```python
calculateFeatures = {
    'A' : True,
    'B' : True,
    'C' : False
}
```
* 'True' means that the Pi will calculate and upload only the features. The table structure will be like the one in the ['sensingdata_A' table below](#table-sensingdataA).
* 'False' means that the Pi will aggregate data and upload it as-is. The table structure will be like the one in the ['sensingdata_C' table](#table-sensingdataC).
* To set the role that each gateway pi will perform, run the script with the appropriate letter, e.g. `$ python3 GatewayPi.py A`

## TABLE : 'sensingdata_A'
* This table is used to store features calculated by Gateway A.
```
'forum'             --> (String)*
                        InitializeAllDBTables.py sets a value of 'roomA'
                        GatewayPi.py searches for 'roomA'
                        TriggerLambda.py searches for 'roomA'

'subject'           --> (String)*
                        InitializeAllDBTables.py sets a value of 'sensorA'
                        GatewayPi.py searches for 'sensorA'
                        TriggerLambda.py searches for 'sensorA'

'feature_A'         --> ('roomA', 'sensorA')
                        Set by GatewayPi.py after local computations
                        Queried by LinearRegressionLambda.py

'feature_B'         --> ('roomA', 'sensorA')
                        Set by GatewayPi.py after local computations
                        Queried by LinearRegressionLambda.py

'feature_C'         --> ('roomA', 'sensorA')
                        Set by GatewayPi.py after local computations
                        Queried by LinearRegressionLambda.py

'Comm_pi_pi'        --> ('roomA', 'sensorA')
                        GatewayPi.py stores bluetooth transfer time
                        Queried by LinearRegressionLambda.py

'Compu_pi'          --> ('roomA', 'sensorA')
                        GatewayPi.py stores the local computation time.
                        Queried by LinearRegressionLambda.py

'Comm_pi_lambda'    --> ('roomA', 'sensorA')
                        GatewayPi.py stores the time taken to upload the data.
                        Queried by LinearRegressionLambda.py

'timeStamp'         --> ('roomA', 'sensorA')
                        GatewayPi.py stores the time at which the upload was completed.
                        Queried by TriggerLambda.py to check if it's time to exit the loop.
                        Queried by LinearRegressionLambda.py

'data_bytes'        --> ('roomA', 'sensorA')
                        GatewayPi.py stores the size of the uploaded data in bytes.
```

## TABLE : 'sensingdata_C'
* This table is used to store the data aggregated from sensor C and gateway C; no features present.
* These keys for the items below are differ in their 'subject' field, e.g.
    `('roomA', '22', 'X_1', 'X_2', ...), ('roomA', '23', 'X_1', 'X_2', ...)`
```
'forum'             --> (String)*
                        InitializeAllDBTables.py sets a value of 'roomA'
                        DemoPlot.py queries for 'roomA'

'subject'           --> (String)*
                        InitializeAllDBTables.py sets a value of 'sensorC'
                        DemoPlot.py queries for '199'

'Comm_pi_lambda'    --> ('roomA', 'sensorC')
                        GatewayPi.py stores the time taken to upload data.

'timeStamp'         --> ('roomA', 'sensorC')
                        GatewayPi.py stores the time at which the upload was completed.                        

'data_bytes'        --> ('roomA', 'sensorC')
                        GatewayPi.py stores the size of the uploaded data in bytes
                        Queried by LinearRegressionLambda.py

'aggregated_data'   --> ('roomA', 'sensorC')
                        GatewayPi.py stores the data in a list of dicts that have the keys:
                            'X_1'   : Time at which the measurement was taken
                            'X_2'   : Atmospheric pressure at that instance
                            'X_3'   : Humidity at that instance
                            'Y'     : Temperature at that instance
```

## TABLE : 'weightresult'
* Stores the results of the AWS Lambda computations.
```
'environment'       --> (String)*
                            InitializeAllDBTables.py sets a value of 'roomA'
                            DemoPlot.py queries for 'roomA'

'sensor'            --> (String)*
                            InitializeAllDBTables.py sets a value of 'sensorA&B&C'
                            DemoPlot.py queries for 'sensorA&B&C'

* All of the keys below are in the ('roomA', 'sensorA&B&C') item
'w_1'               --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
'w_2'               --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
'Prediction'        --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
'Error'             --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
'Lambda_ExecTime'   --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
'Time'              --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
'Comm_pi_pi'        --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
'Comm_pi_lambda'    --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
'Compu_pi'          --> ('roomA', 'sensorA&B&C')
                        LinearRegressionLambda.py
```

## TABLE : 'Trigger_A'
* The AWS Lambda function listens to this table.
* If the table gets updated, the function will start running.
```
'forum'             --> (String)*
                        InitializeAllDBTables.py sets a value of
                        TriggerLambda.py searches for 'roomA',

'subject'           --> (String)*
                        InitializeAllDBTables.py sets a value of
                        TriggerLambda.py searches for '1'

'timeStamp'         --> Set by TriggerLambda.py
```
