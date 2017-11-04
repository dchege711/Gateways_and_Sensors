# Gateways and Sensors
* This repository houses the code used to test out concepts covered in the Decomposing Data Analytics in Fog Networks paper.

### The "cloud_vs_fog" branch
* This branch allows side-by-side comparison of a cloud implementation and a fog implementation.
* When the experiment is run, two inner runs are made, one using cloud resources, and one using fog resources.
* At the end of each experiment, the two are compared using a table.

### Useful links:
* [Getting Started Notes](https://github.com/dchege711/Gateways_and_Sensors/blob/master/Getting_Started.md)
* [Replicating the Experiment](#replicating-the-experiment)
* [Description of Files](https://github.com/dchege711/Gateways_and_Sensors/blob/master/Description_of_Files.md)

----

## Replicating the Experiment
* Perform the following steps for initialization (once only for every AWS account):
    * `$ python3 InitializeAllDBTables.py` to set up all DynamoDB tables.
    * Upload the .zip file that contains LinearRegressionLambda.py to AWS Lambda. ([Instructions on creating a python .zip deployment package](http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html))

## Notes for SenSys 2017

### Preparing the Experiment
* To clone the repo, use `$ git clone https://github.com/dchege711/Gateways_and_Sensors.git`
* On your laptop, navigate to the Gateways_and_Sensors folder on the command line: `cd Gateways_and_Sensors`
* Ensure that you're on the right branch by running `$ git branch`. The asterisk should be on the cloud_vs_fog branch.
    * In case you don't have the cloud_vs_fog branch, run `$ git checkout -b cloud_vs_fog`.
    * If you have the cloud_vs_fog branch, but the asterisk isn't on it, run `$ git checkout cloud_vs_fog`
* Update the code on your laptop to the latest version by running `$ git pull origin cloud_vs_fog`

* Remark: The Pis are on the cloud_vs_fog branch. There's no need to run these commands on the Pis. Furthermore, the code that the Pis care about hasn't changed since Fog World Congress. If you need to change any of the code that runs on the Pis, do it from Github and then pull those changes. If you do it on the Pi, you might incur some merge conflicts and permission issues later on.
    * On each the Pis run `$ cd Gateways_and_Sensors` to navigate to the appropriate folder. 
    * You could also confirm that you're on the cloud_vs_fog branch by running `$ git branch`


### Running the Experiment
* For each of the pairs, start from the Gateway and then finish with the Sensor. 
    * On the Gateway, set Bluetooth to 'discoverable' and ensure that Wi-Fi is on. Then run `$ python GatewayPi.py A 5`
        * On the command line, you should see "Fetched sampleSize table..."
        * On the SenseHats, you should observe the "G" symbol and then an arrow (the arrow means it's waiting for data from the sensor pi)
    * On the corresponding Sensor, ensure that Wi-Fi is on and run `$ python SensorPi.py A 5`
        * On the command line, you should see "Fetched sampleSize table..."
        * On the SenseHats, you should observe the "S" symbol, and then after a few seconds, some green pluses (collecting data) and then an arrow (sending data to the Gateway via Bluetooth)
        * The Gateway Pi should then respond by receiving the data (the corner dots of the LEDs turn to blue), collecting its own set of readings (green pluses) and then uploading them to the cloud (blue arrow).
    * Repeat these steps for pairs B and C, i.e.
        * Bluetooth --> Discoverable, Wi-Fi on, `$ python GatewayPi.py B 5`, `python SensorPi.py B 5`
        * Bluetooth --> Discoverable, Wi-Fi on, `$ python GatewayPi.py C 5`, `python SensorPi.py C 5`

* Common Pi Troubleshooting Steps:
    * `Bluetooth error: Host is down...`
        * Ensure that the Gateway's Bluetooth is on discoverable. 
        * Sometimes it's due to synchronization issues (the sensor tried sending when the gateway wasn't listening). The 5 seconds in `$ python GatewayPi.py B 5` tends to avoid such mis-timings, but it's not perfect.
        * GatewayPi.py might still be running even after SensorPi.py reports this error. 
        * The workaround is quitting the GatewayPi.py instance and then re-running the `$ python GatewayPi.py <letter> 5`, `python SensorPi.py <letter> 5` sequence.
        * If this doesn't work, then my guess is that you're dealing with the wrong Pi as Gateway A. Remember how we had trouble updating Gateway A? So ensure that you have the right Gateway A. I don't remember how to identify it :-(
    * `Table not found. Need a new hash key...`
        * This is usually caused by the pis not reading the credentials contained in the environment variables.
        * Try running `$ source ~.bashrc` to force a refresh and then re-run the `$ python GatewayPi.py <letter> 5`, `python SensorPi.py <letter> 5` sequence.
        * If that doesn't work, reboot the Pi. Sometimes I had to reboot twice :-(

* On your laptop:
    * You'll need two separate command line windows.
    * In the first window, run `$ python TriggerLambda.py`
        * This script calls AWS Lambda whenever all 3 Gateways submit their data, and then displays the approximated cost, latency and error for each run.
    * In the second window, run `$ python Button.py`
        * This script allows you to set the number of readings that will be taken by each sensor. (Remember that the Gateway also acts as a sensor since it makes readings as well.)
        * You should see a GUI that allows you to submit a number. After about 5 seconds (since we told the Pis to check AWS every 5 seconds), you should see the Pis respond to the new command.
        * After all is done, you should see the cost, latency and error data logged to the command line.
        * Any time you need to demo, enter a number into the GUI and click "Enter".
