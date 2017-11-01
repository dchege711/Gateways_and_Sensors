from DynamoDBUtility import Table

def fetch_data(gateway_letter, subject_val):
	table = Table('sensingdata_' + gateway_letter)
	data = table.getItem({
		"forum" : "roomA",
		"subject" : subject_val
	})

	return data["aggregated_data"]

def add_data(gateway_letter, new_data):
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


if __name__ == "__main__":
	data_A = fetch_data('A', "1509487184.48")
	data_B = fetch_data("B", "1509487184.39")
	data_C = fetch_data("C", "1509487185.05")

	add_data("A", data_A)
	add_data("B", data_B)
	add_data("C", data_C)