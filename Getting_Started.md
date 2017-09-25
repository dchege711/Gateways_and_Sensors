## Getting Started
* I'm using python 2.7 on the Pi. There are compatibility issues with python3, especially with pybluez. To check the default python version, use `$ python --version`
    * If you need to change to python2, see the instructions on this [site](https://linuxconfig.org/how-to-change-from-default-to-alternative-python-version-on-debian-linux#h2-change-python-version-system-wide).
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