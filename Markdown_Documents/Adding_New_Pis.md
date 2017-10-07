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
4. Include the Pi(s) bluetooth address(es) into BluetoothUtility.py
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