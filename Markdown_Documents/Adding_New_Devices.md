## Adding New Pis
* To add a new Pi to the setup, follow the following steps.

1. Install Raspbian on the Pi
	* Follow the instructions from the [official documentation](https://www.raspberrypi.org/downloads/).
2. Store AWS credentials in the bash profile.
	* Run `$ nano ~.bashrc` to open the bash profile.
	* Include these variables at the bottom of the bash profile as follows:
	````
	# AWS CREDENTIALS
	export aws_access_key_id="AKIA..."
	export aws_secret_access_key="5Ky....."
	````
3. Clone the repository from Github.
	* Run `$ git clone https://github.com/dchege711/Gateways_and_Sensors.git`
	* Run `$ cd Gateways_and_Sensors` to move into the created folder.
4. Install all the required packages.
	* Run `$ sudo pip install -r pi_pacakages.txt`
	* Some packages need to be installed using apt-get. See [pi_aptget_packages.txt] for more information.
5. Include the Pi(s) bluetooth address(es) into BluetoothUtility.py
	````
	...
	gatewayBRAddresses = {
		...
    	'C' : 'B8:XX:XX:XX:XX:09'	# The added pi will function as Gateway C
    	....
	}

	sensorBRAddresses = {
    	...
	}
	````

## Adding a Laptop as a Control Center
1. Install Python (we're using 2.7) and Git.
2. Clone the Github repo as described in step #3 above.
3. Securely store the AWS credentials as environment variables using the same keys as in step #2 above.
4. Restart the terminal so that the environment variables can take effect.
5. Run `$ python DemoPlot.py` while inside the /Gateways_and_Sensors directory to ensure that you've not missed anything. You should see a UI box that allows you to set the number of samples to be taken by the sensors.
