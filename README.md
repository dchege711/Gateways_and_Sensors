# Gateways and Sensors
* This repository houses the code used to test out concepts covered in the Decomposing Data Analytics in Fog Networks paper.
* A few notes on the puporse of each branch in this repo:
    * **master**
        * Contains the code up to Sept 25th before we decided to explore other possibilities.
    * **humidity_prediction**
        * Instead of predicting temperature, we'll be predicting humidity from temperature and air pressure.
    * **all_cloud**
        * In this branch, the Pis do no computations. Everything is done on the cloud.
        * Remember to set the appropriate link to the code .zip file on AWS Lambda.
        * This allows a comparison to the decomposition that this experiment advocates.
    * **no_wifi**
        * Anticipates periods of poor connectivity during demonstrations. 
        * This runs a simulation of the experiment without invoking AWS.
        * Plan: Make the laptop do act like the cloud so that the simulation is more realistic.
* Useful links:
    * [Getting Started Notes](https://github.com/dchege711/Gateways_and_Sensors/blob/master/Getting_Started.md)
    * [Replicating the Experiment](#replicating-the-experiment)
    * [Description of Files](https://github.com/dchege711/Gateways_and_Sensors/blob/master/Description_of_Files.md)

----

## Replicating the Experiment
* Perform the following steps for initialization (once only for every AWS account):
    * `$ python3 InitializeAllDBTables.py` to set up all DynamoDB tables.
    * Upload the .zip file that contains LinearRegressionLambda.py to AWS Lambda. ([Instructions on creating a python .zip deployment package](http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html))
* Run the following scripts in the order below:
    * `$ git pull origin <branch_name>` on each pi to make sure you have the most recent code.
    * `$ python SensorPi.py <letterDenotingTheSensor> <sleepTimeInSeconds>` on the Pis designated as sensors.
    * `$ python GatewayPi.py <letterDenotingTheGateway> <sleepTimeInSeconds>` on the Pis designated as gateways.
* On the laptop, run the programs below, preferably in separate terminal windows.
    * `$ python Button.py` 
        * Enter the number of data points to be collected.
        * This triggers the sensors and the gateways.
    * `$ python TriggerLambda.py`
        * This triggers AWS Lambda as soon as all gateways are done.
    * `$ python DemoPlot.py`
        * The table will update itself with the experiment's results.
---
