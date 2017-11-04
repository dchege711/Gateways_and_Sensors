"""
This script is not needed for the experiment. I wrote it so as to test a few
things on the database. 

There's no harm in ignoring it.

"""

from DynamoDBUtility import Table
from lambda_utility import aws_lambda
import LinearRegressionLambdaLocal as local_lambda

lambda_client = aws_lambda()

def fetch_data(gateway_letter, subject_val):
	"""
	Each set of readings is stored using "roomA" and a timeStamp string.
	This method provides a convenient way for retrieving past readings.

	The timeStamp strings are found in the items of the 'weightresults' table. 

	"""
	table = Table('sensingdata_' + gateway_letter)
	data = table.getItem({
		"forum" : "roomA",
		"subject" : subject_val
	})

	return data["aggregated_data"]

def add_data(gateway_letter, new_data):
	"""
	Modify the data entry that gradient descent and linear regression use
	as the source of their data.

	Useful when you wish to simulate a previous run of the experiment.

	"""
	table = Table("sensingdata_" + gateway_letter)
	item = table.getItem({
		"forum" : "roomA",
		"subject" : "sensor" + gateway_letter
	})

	item["aggregated_data"] = new_data
	item.pop('feature_A', None)
	item.pop('feature_B', None)
	item.pop('feature_C', None)
	table.addItem(item)

def test_accuracy():
	"""
	Quite a misnomer. Doesn't really test the accuracy.

	Print out the MSE observed in various runs of the experiment.
	
	"""
	i = 0
	num_tests = 1
	while (i < num_tests):

		response_cloud = lambda_client.invoke("LinearRegressionLambda")
		print("\nPrinting summary of results...\n")
		print("w_1 and w_2", str(response_cloud["w_1"]), str(response_cloud["w_2"]))
		print("Error :", str(response_cloud["Error"]))
		print("Source :", str(response_cloud["fog_or_cloud"]))
		print()
		response_local = local_lambda.lambda_handler(1, 1)
		i += 1

def print_accuracies():
	table = Table('weightresult')
	item = get_all_results()

	accuracies = {}
	accuracies["fog (edge + cloud)"] = {}
	accuracies["all_cloud"] = {}

	for result in item["results"]:
		accuracy_reading = '{0:.2f}'.format(float(result["Error"]))
		size_of_data = result["readings_per_sensor"]
		# print(result)
		if result["fog_or_cloud"] == "all_cloud":
			if size_of_data not in accuracies["all_cloud"]:
				accuracies["all_cloud"][size_of_data] = []
			accuracies["all_cloud"][size_of_data].append(accuracy_reading)
		else:
			if size_of_data not in accuracies["fog (edge + cloud)"]:
				accuracies["fog (edge + cloud)"][size_of_data] = []
			accuracies["fog (edge + cloud)"][size_of_data].append(accuracy_reading)

	print("\nAll Cloud Results...\n")
	for key in accuracies["all_cloud"].keys():
		print(key, accuracies["all_cloud"][key])

	print("\nFog Results...\n")
	for key in accuracies["fog (edge + cloud)"].keys():
		print(key, accuracies["fog (edge + cloud)"][key])

def get_all_results(sensor_val="cloud_vs_fog"):
	table = Table('weightresult')
	results = table.getItem({
		"environment" : "roomA",
		"sensor" : sensor_val
	})
	return results["results"]
	

def test():
	data_A = fetch_data('A', "1509487184.48")
	data_B = fetch_data("B", "1509487184.39")
	data_C = fetch_data("C", "1509487185.05")

	add_data("A", data_A)
	add_data("B", data_B)
	add_data("C", data_C)

	test_accuracy()

if __name__ == "__main__":
	# print_accuracies()
	print_expected_observations()