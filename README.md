### Possible Next Steps:
* Implement a function that plots all the collected data so far versus number of samples, i.e. bluetooth latency, database upload latency, storage and computational costs, etc.

-----

# Gateways and Sensors Experiment
* This repository houses the code used to test out a fog setup with Raspberry Pis.
    * [Getting Started Notes](#getting-started-notes)
    * [Replicating the Experiment](#replicating-the-experiment)
    * [Description of Files](#description-of-files)

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
