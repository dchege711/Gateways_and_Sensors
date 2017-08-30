### Next Steps:
* Resolve the timing out on AWS. Relax table capacities(?)
* Implement a function that plots all the collected data so far.

# Gateways and Sensors Experiment
* This repository houses the code used to test out a fog setup with Raspberry Pis.
    * [Getting Started Notes](#getting-started-notes)
    * [Replicating the Experiment](#replicating-the-experiment)
    * [Description of Files](#description-of-files)

----

## Getting Started Notes
* I'm using python3 on the Pi. To check the default python version, use `$ python --version`
    * If you need to change to python3, see the instructions on this [site](https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux#h2-change-python-version-system-wide).
* To connect to AWS services, you must present credentials. The code assumes that you have environment variables named 'aws_access_key_id' and 'aws_secret_access_key'. To set these variables:
    * Open the bash profile on the pi using `$ nano ~/.bashrc`
    * Add the AWS credentials into the bash profile as below:
        ```shell
        # AWS CREDENTIALS
        export aws_access_key_id="XXXXXX"
        export aws_secret_access_key="XXXXX"
        ```
    * To avail these variables within the same command prompt session without restarting the command prompt, run the command `$ source ~/.bashrc`
* Clone the repository using `$ git clone https://github.com/dchege711/Gateways_and_Sensors.git`. Navigate to the created directory using `$ cd Gateways_and_Sensors`
* Tip: Under the Pis bluetooth settings, make them discoverable. This avoids many connection hassles.

----

## Replicating the Experiment
* Perform the following steps for initialization (once only for every AWS account):
    * `$ python3 InitializeAllDBTables.py` to set up all DynamoDB tables.
    * Upload the .zip file that contains LinearRegressionLambda.py to AWS Lambda. ([Instructions on creating a python .zip deployment package](http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html))
* Run the following scripts in the order below:
    * `$ python3 SensorPi.py <letterDenotingTheSensor> <sleepTimeInSeconds>` on the Pis designated as sensors.
    * `$ python3 GatewayPi.py <letterDenotingTheGateway> <sleepTimeInSeconds>` on the Pis designated as gateways.
    * `$ python3 Button.py` on your laptop. Enter the number of data points to be collected.
        * This triggers the sensors and the gateways.
    * `$ python3 TriggerLambda.py` on your laptop.
        * This triggers AWS Lambda as soon as all gateways are done.
    * `$ python3 DemoPlot.py` on your laptop.
        * The table will update itself with the experiment's results.
---

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
