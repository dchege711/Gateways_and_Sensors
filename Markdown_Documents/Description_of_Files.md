## Description of Files

### [SensorPi.py](https://github.com/dchege711/Gateways_and_Sensors/blob/master/SensorPi.py)
* Executed in the Pis that act as sensors (data collectors).
* Collects temperature, pressure and humidity data and pushes it to the corresponding Gateway Pi via Bluetooth.

### [TriggerLambda.py](https://github.com/dchege711/Gateways_and_Sensors/blob/master/TriggerLambda.py)
* Can be ran on any device in the setup (sensor, gateway or laptop)
* Checks whether all three Gateway Pis have completed their transmission to AWS.
* It then updates a DynamoDB table that has been specified as a trigger for an AWS Lambda function.

### [Button.py](https://github.com/dchege711/Gateways_and_Sensors/blob/master/Button.py)
* Can be ran on any device in the setup (sensor, gateway or laptop)
* Sets the number of data samples to be taken and stores this number in a DynamoDB table.
* Once the sensors and gateways detect this change, they'll escape their while loops and start performing their respective roles.

### [DemoPlot.py](https://github.com/dchege711/Gateways_and_Sensors/blob/master/DemoPlot.py)
* Can be ran on any device in the setup (sensor, gateway or laptop)
* Fetches data from DynamoDB and presents it as a matplotlib visualization.

### [GatewayPi.py](https://github.com/dchege711/Gateways_and_Sensors/blob/master/GatewayPi.py)
* Executed in the Pis that act as gateways (data aggregators and pre-processors).
* Gateway 1 and 2 calculate features from Sensor Pi data, and transmits them to DynamoDB, bearing higher computational latency.
* Gateway 3 transmits sensor data that it collects, bearing higher transmission latency.

### [InitializeAllDBTables.py](https://github.com/dchege711/Gateways_and_Sensors/blob/master/InitializeAllDBTables.py)
* Can be ran on any device in the setup (sensor, gateway or laptop)
* Creates all the DynamoDB tables needed by the experiment, with the expected pre-filled data.

### [LEDManager.py](https://github.com/dchege711/Gateways_and_Sensors/blob/master/LEDManager.py)
* This is not executed, but must exist in the Raspberry Pis. Other scripts import it.
* A helper script for adjusting the patterns on the sense hat LEDs.

### [LinearRegressionLambda.py](https://github.com/dchege711/Gateways_and_Sensors/blob/master/LinearRegressionLambda.py)
* A linear regression model that runs on AWS Lambda.
* It is triggered by the DynamoDB table that is updated by TriggerLambda.py

### [requirements.txt](https://github.com/dchege711/Gateways_and_Sensors/blob/master/requirements.txt)
* Contains a list of all the packages needed to run the experiment.
* You can use `$ pip install -r requirements.txt` to ensure that you have everything that's needed.
    * As of 11th Aug 2017, pybluez is unstable on OS X. But it installs in the Pi (Debian). You'll only need pybluez on the Pi for Bluetooth data transfer.