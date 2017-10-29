"""
Centralized location for handling all requests to AWS Lambda

@ Original Author	: Chege Gitau

"""

import boto3
import os
from botocore.exceptions import ClientError
import time
import json

client = boto3.client(
    'lambda',
    aws_access_key_id = os.environ['aws_access_key_id'],
    aws_secret_access_key = os.environ['aws_secret_access_key'],
    region_name = 'us-east-1'
)

class aws_lambda:

	# Currently, we don't have any use for initialization

	def get_function(self, function_name, qualifier=None):

		if qualifier is not None:
			response = client.get_function(
				FunctionName=function_name,
				Qualifier=qualifier
			)
		else:
			response = client.get_function(
				FunctionName=function_name
			)

		return response

	def invoke(self, function_name, invocation_type="RequestResponse"):
		response = client.invoke(
			FunctionName=function_name,
			InvocationType=invocation_type
		)
		return json.loads(response['Payload'].read())

	def list_all_functions(self):
		response = client.list_functions()

def test():
	my_lambda = aws_lambda()

	print("\nTesting the get_function() method...")
	print(my_lambda.get_function("DiceScore"))

	print("\nTesting the list_all_functions() method...")
	print(my_lambda.list_all_functions())

	print("\nTesting the invoke() method...")
	startTime = time.time()
	response = my_lambda.invoke("LinearRegressionLambda")
	endTime = time.time()
	for key in response.keys():
		print(key, "\t:", response[key])
	print("\nInvocation took", str(endTime-startTime), "seconds.")


if __name__ == "__main__":
	test()

