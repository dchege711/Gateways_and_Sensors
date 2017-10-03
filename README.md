# Gateways and Sensors
* This repository houses the code used to test out concepts covered in the Decomposing Data Analytics in Fog Networks paper.

### The "humidity_prediction" branch
* Instead of predicting temperature, we'll be predicting humidity from temperature and air pressure.
* We wish to test whether changing the target feature leads to better predictions.

### Useful links:
* [Getting Started Notes](https://github.com/dchege711/Gateways_and_Sensors/blob/master/Getting_Started.md)
* [Replicating the Experiment](#replicating-the-experiment)
* [Description of Files](https://github.com/dchege711/Gateways_and_Sensors/blob/master/Description_of_Files.md)

----

## Replicating the Experiment
* Perform the following steps for initialization (once only for every AWS account):
    * `$ python3 InitializeAllDBTables.py` to set up all DynamoDB tables.
    * Upload the .zip file that contains LinearRegressionLambda.py to AWS Lambda. ([Instructions on creating a python .zip deployment package](http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html))
* Run the following scripts in the order below:
    * **Github pull**
    * `$ python3 SensorPi.py <letterDenotingTheSensor> <sleepTimeInSeconds>` on the Pis designated as sensors.
    * `$ python3 GatewayPi.py <letterDenotingTheGateway> <sleepTimeInSeconds>` on the Pis designated as gateways.
* On the laptop, run the programs below, preferably in separate terminal windows.
    * `$ python3 Button.py` 
        * Enter the number of data points to be collected.
        * This triggers the sensors and the gateways.
    * `$ python3 TriggerLambda.py`
        * This triggers AWS Lambda as soon as all gateways are done.
    * `$ python3 DemoPlot.py`
        * The table will update itself with the experiment's results.
---
