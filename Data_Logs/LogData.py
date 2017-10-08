"""
Fetches all the data that's logged by the all_cloud branch.
It then makes tab-delimited text files out of that data. 
Useful for analayzing why some runs have lower accuracy than others
"""

import sys
sys.path.insert(0, "C:/Users/dchege711/Gateways_and_Sensors")

from DynamoDBUtility import Table

def get_file_name(error, label, readings_per_gateway):
	"""
	Set the naming format of the data files.
	"""
	error = str('{:.2f}'.format(error)).replace('.', '_')
	return ''.join([error, "_", label, "_", readings_per_gateway, ".txt"])

def log_from_table(experiment_data, key, error, readings_per_gateway):
	"""
	Create a text file for a given gateway and log all its readings
	in the given run of the experiment.

	"""
	filename = get_file_name(error, key, readings_per_gateway)
	items = experiment_data[key]
	print("Logging", filename)
	with open(filename, 'w') as dataFile:
		dataFile.write(str(error) + "\t" + str(readings_per_gateway) + "\n")
		dataFile.write("time\tpressure\thumidity\ttemperature\n")
		for item in items:
			dataFile.write(
				str(item['X_1']) + "\t" +
				str(item['X_2']) + "\t" +
				str(item['X_3']) + "\t" +
				str(item['Y']) + "\n"
			)


def main():
	"""
	Execute the main logic of this program.

	"""
	dataTable = Table('weightresult')
	data = dataTable.getItem({'environment': 'roomA', 'sensor': 'all_cloud_results'})['results']
	size_of_one_reading = 32

	for experiment_data in data:
		error = float(experiment_data['Error'])
		readings_per_gateway = str(experiment_data['data_bytes_entire'] / size_of_one_reading)
		
		# Record data from Gateway A
		log_from_table(experiment_data, "gateway_A", error, readings_per_gateway)
		log_from_table(experiment_data, "gateway_B", error, readings_per_gateway)
		log_from_table(experiment_data, "gateway_C", error, readings_per_gateway)
	 
if __name__ == "__main__":
	main()

