"""
Centralized location for handling all requests to AWS Lambda

@ Original Author	: Chege Gitau

"""

import boto3
import os
from botocore.exceptions import ClientError

aws_lambda = boto3.resource(
    'lambda',
    aws_access_key_id = os.environ['aws_access_key_id'],
    aws_secret_access_key = os.environ['aws_secret_access_key'],
    region_name = 'us-east-1'
)

class aws_lambda:

	def __init__(self):
		# Currently, we have no need for initialization.
		self.aws_lambda = None

	def get_function(self, function_name, qualifier=None):

		if qualifier not None:
			response = aws_lambda.get_function(
				FunctionName=function_name,
				Qualifier=qualifier
			)
		else:
			response = aws_lambda.get_function(
				FunctionName=function_name,
			)

		return response

	def invoke(self, function_name, invocation_type="RequestResponse"):
		response = aws_lambda.invoke(
			FunctionName=function_name,
			InvocationType=invocation_type
		)
		return response
		
