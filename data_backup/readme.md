## Readme

* I used `download_dynamo_db_data.py` to download the data from DynamoDB. 
* The setup had 6 raspberry pis that were grouped in pairs A, B and C. 
* In each pair, one pi acted as the gateway (that connected to AWS and/or processed the data), while the other acted as a sensor (that only collected data)

#### sensingdata_A_cloud_compute.csv, sensingdata_B_cloud_compute.csv, sensingdata_C_cloud_compute.csv

* In this case, the pis were forwarding all their data to the cloud for processing. 
* The CSVs are comma-delimited without spaces:
    * `timestamp,N`
    * N lines of the format: `time, pressure, humidity, temperature`
    * ...
    * `timestamp,N`
    * N lines of the format: `time, pressure, humidity, temperature`
    * ...
* Each group of timestamp + N readings came from a separate run of the experiment.
* The timestamp alongside the N denotes the time at which that experiment started. 
* This timestamp was also used to as an ID when analyzing the data from a given run of the experiment.

#### sensingdata_A_local_compute.csv, sensingdata_B_local_compute.csv

* The pis in group C never had to run the gradient descent algorithm locally, thus no file exists for them.
* You'll also note that the files have only one line. This happened because of overwriting old data. 
* Not to worry though, the data from each run was stored in the next section.

#### fog_results.csv, all_cloud_results.csv

* You'll probably be most interested in this section.
* Both files have the same format where each line follows the pattern:
    * `timestamp_id_to_A, timestamp_id_to_B, timestamp_id_to_C, latency_between_sensor_and_gateway_pi_in_seconds, latency_between_gateway_pi_and_lambda_in_seconds, time_spent_computing_on_the_pi, time_spent_computing_on_lambda, linear_regression_param_one, linear_regression_param_two, number_of_bytes_sent_by_gateways_A_and_B_to_the_cloud, total_number_of_bytes_sent_to_the_cloud, number_of_sensors_available, mean_square_error_in_the_predicted_temperature`

Cheers!
Chege