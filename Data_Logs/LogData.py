"""
Fetches all the data that's logged by the all_cloud branch.
It then makes tab-delimited text files out of that data. 
Useful for analayzing why some runs have lower accuracy than others
"""

import sys
sys.path.insert(0, "C:/Users/dchege711/Gateways_and_Sensors")

from DynamoDBUtility import Table

# Pre-load the data tables
table_A = Table('sensingdata_A')
table_B = Table('sensingdata_B')
table_C = Table('sensingdata_C')
dataTable = Table('weightresult')

def get_file_name(error, label, readings_per_gateway):
	"""
	Set the naming format of the data files.
	"""
	error = str('{:.2f}'.format(error)).replace('.', '_')
	return ''.join([error, "_", label, "_", readings_per_gateway, ".txt"])

def log_from_table(gateway_subject, gateway_letter, error, readings_per_gateway):
	"""
	Create a text file for a given gateway and log all its readings
	in the given run of the experiment.

	"""
	filename = get_file_name(error, gateway_letter, readings_per_gateway)

	# Fetch the appropriate dataset from DynamoDB
	if gateway_letter == "gateway_A":
		appropriate_table = table_A
	elif gateway_letter == "gateway_B":
		appropriate_table = table_B
	elif gateway_letter == "gateway_C":
		appropriate_table = table_C
	else:
		error_msg = " ".join([
			gateway_letter, 
			"is invalid. Try 'gateway_A', 'gateway_B' or 'gateway_C'"
		])
		raise ValueError(error_msg)
	items = appropriate_table.getItem({'forum': 'roomA', 'subject': gateway_subject})
	
	try:
		items = items['aggregated_data']
	except KeyError:
		print("Missing", gateway_letter, gateway_subject)
		return


	print("Logging", filename)
	with open(filename, 'w') as data_file:
		data_file.write(str(error) + "\t" + str(readings_per_gateway) + "\n")
		data_file.write("time\tpressure\thumidity\ttemperature\n")
		for item in items:
			data_file.write(
				str(item['X_1']) + "\t" +
				str(item['X_2']) + "\t" +
				str(item['X_3']) + "\t" +
				str(item['Y']) + "\n"
			)

def log_all_cloud_stats():
	data = dataTable.getItem({'environment': 'roomA', 'sensor': 'all_cloud_results'})['results']
	size_of_one_reading = 32

	print("Logging stats from the all_cloud experiment...")
	filename = "all_cloud_stats.txt"

	with open(filename, 'w') as data_file:
		data_file.write("N_used_for_prediction\terror\tupload_time\tbluetooth_time\tpi_compute_time\tlambda_compute_time\n")
		for item in data:
			readings_per_sensor = str(item['data_bytes_features'] / size_of_one_reading)
			data_file.write(
				readings_per_sensor + "\t" +
				str(item['Error']) + "\t" +
				str(item['Comm_pi_lambda']) + "\t" +
				str(item['Comm_pi_pi']) + "\t" +
				str(item['Compu_pi']) + "\t" +
				str(item['Lambda_ExecTime']) + "\n"
			)

	print("Successfully logged data to", filename)


def log_sensor_data():
	"""
	Execute the main logic of this program.

	"""
	
	data = dataTable.getItem({'environment': 'roomA', 'sensor': 'all_cloud_results'})['results']
	size_of_one_reading = 32

	for experiment_data in data:

		error = float(experiment_data['Error'])
		readings_per_gateway = str(experiment_data['data_bytes_entire'] / size_of_one_reading)
		
		gateway_A_subject = experiment_data['gateway_A_subject']
		gateway_B_subject = experiment_data['gateway_B_subject']
		gateway_C_subject = experiment_data['gateway_C_subject']

		log_from_table(gateway_A_subject, "gateway_A", error, readings_per_gateway)
		log_from_table(gateway_B_subject, "gateway_B", error, readings_per_gateway)
		log_from_table(gateway_C_subject, "gateway_C", error, readings_per_gateway)


	 
if __name__ == "__main__":
	# log_sensor_data()
	log_all_cloud_stats()

