"""
A script for downloading the data that is on DynamoDB. This is necessary 
because DynamoDB cannot export large files to CSV.

"""
import json
from pprint import pprint
from DynamoDBUtility import Table

def dump_data():
    table_names = [
        "sensingdata_A", "sensingdata_B", "sensingdata_C"
    ]

    for table_name in table_names:
        print("Scanning", table_name)
        dynamo_table = Table(table_name)

        cloud_compute_output = open(table_name + "_cloud_compute.csv", "w")
        local_compute_output = open(table_name + "_local_compute.csv", "w")
        
        i = 0
        for page in dynamo_table.getAllItems():
            for item in page["Items"]:
                try:
                    if "aggregated_data" in item.keys():

                        output_line = ",".join([
                            item["subject"]["S"], 
                            str(len(item["aggregated_data"]["L"]))
                        ])
                        cloud_compute_output.write(output_line + "\n")

                        for reading in item["aggregated_data"]["L"]:
                            output_line = ",".join([
                                reading["M"]["X_1"]["N"],
                                reading["M"]["X_2"]["N"],
                                reading["M"]["X_3"]["N"],
                                reading["M"]["Y"]["N"]
                            ])
                            cloud_compute_output.write(output_line + "\n")

                    elif table_name in {"sensingdata_A", "sensingdata_B"}:
                        
                        output_line = ",".join([
                            item["forum"]["S"],
                            item["subject"]["S"],
                            item["timeStamp"]["N"],
                            item["feature_A"]["N"],
                            item["feature_B"]["N"],
                            item["feature_C"]["N"],
                            item["Comm_pi_pi"]["N"],
                            item["data_bytes"]["N"],
                            item["Comm_pi_lambda"]["N"],
                            item["number_of_sensors"]["N"],
                            item["Compu_pi"]["N"]
                        ])
                        local_compute_output.write(output_line + "\n")

                except KeyError:
                    print(item.keys())
                    break
                
                
                i += 1
                if (i % 50 == 0):
                    print("Appended", i, "documents")

def dump_results():
    dynamo_table = Table("weightresult")
    all_cloud_results_output = open("all_cloud_results.csv", "w")
    fog_results_output = open("fog_results.csv", "w")

    for s_string in ["all_cloud_results", "cloud_vs_fog"]:
        item = dynamo_table.getItem({
            "environment": "roomA", 
            "sensor": s_string
        })

        for result in item["results"]:
            output_line = ",".join([
                result["gateway_A_subject"], result["gateway_B_subject"], 
                result["gateway_C_subject"], str(result["Comm_pi_pi"]), 
                str(result["Comm_pi_lambda"]), str(result["Compu_pi"]),
                str(result["Lambda_ExecTime"]), str(result["w_1"]), 
                str(result["w_2"]), str(result["data_bytes_features"]), 
                str(result["data_bytes_entire"]),
                str(result["number_of_sensors"]), str(result["Error"])  
            ])

            if ("fog_or_cloud" in result and result["fog_or_cloud"] != "all_cloud"):
                fog_results_output.write(output_line + "\n")
            else:
                all_cloud_results_output.write(output_line + "\n")

if __name__ == "__main__":
    # dump_data()
    dump_results()

             
        




