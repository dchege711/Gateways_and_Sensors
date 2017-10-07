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