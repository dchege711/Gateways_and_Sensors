'''
A linear regression model that runs on AWS Lambda

AWS needs a zip file because it doesn't have numpy (so I can't use the console editor)
Make sure the zip file name, .py name and the handler name on Lambda coincide.

@ Original Author :	Liang Zheng
@ Modified by	  : Chege Gitau

'''

#_______________________________________________________________________________

import boto3
import numpy as np
import decimal
from decimal import *
import time

#_______________________________________________________________________________

def lambda_handler(event, context):
	# Fetch the DynamoDB resource
	tStart = time.time()
	dynamo = boto3.resource('dynamodb')

	# Change: Getting the number of samples from the 'SampleSize' table is tricky
	# When we'll have multiple Pi's, keeping track of this number will be buggy
	# For this reason, I'm setting the value of 'datanum' to the number of items
	# that we're going to get from the table containing the aggregated sensor data

	# Initialize helper variables
	featurenum = 3
	collectornum = 2
	betam = np.zeros((featurenum,collectornum))
	dataBytesFeatures = 0

	# Fetch the features calculated by Gateway A
	table_A = dynamo.Table('sensingdata_A')
	itemKey = {'forum' : 'roomA', 'subject' : 'sensorA'}
	item_A = table_A.get_item(Key = itemKey)['Item']
	betam[0][0] = item_A['feature_A']
	betam[1][0] = item_A['feature_B']
	betam[2][0] = item_A['feature_C']
	dataBytesFeatures += item_A['data_bytes']

	# Fetch the features calculated by Gateway B
	table_B = dynamo.Table('sensingdata_B')
	itemKey = {'forum' : 'roomA', 'subject' : 'sensorB'}
	item_B = table_B.get_item(Key = itemKey)['Item']
	betam[0][1] = item_B['feature_A']
	betam[1][1] = item_B['feature_B']
	betam[2][1] = item_B['feature_C']
	dataBytesFeatures += item_B['data_bytes']

	# Fetch the aggregated data from Gateway C

	table_C = dynamo.Table('sensingdata_C')
	itemKey = {'forum' : 'roomA', 'subject' : 'sensorC'}
	item_C = table_C.get_item(Key = itemKey)['Item']
	aggregatedData = item_C['aggregated_data']
	data_bytes_entire = item_C['data_bytes']

	datanum = len(aggregatedData)
	X = np.zeros((datanum,featurenum))
	y = np.zeros((datanum,1))
	for i in range(datanum):
		X[i][0] = aggregatedData[i]['X_1']
		X[i][1] = aggregatedData[i]['X_2']
		X[i][2] = aggregatedData[i]['X_3']
		y[i][0] = aggregatedData[i]['Y']


	# Compute the maximum bluetooth latency
	Comm_pi_pi_A = item_A['Comm_pi_pi']
	Comm_pi_pi_B = item_B['Comm_pi_pi']
	Comm_pi_pi_C = item_C['Comm_pi_pi']
	Comm_pi_pi = np.max([Comm_pi_pi_A, Comm_pi_pi_B, Comm_pi_pi_C])

	# Compute the maximum upload latency
	Comm_pi_lambda_A = item_A['Comm_pi_lambda']
	Comm_pi_lambda_B = item_B['Comm_pi_lambda']
	Comm_pi_lambda_C = item_C['Comm_pi_lambda']
	Comm_pi_lambda = np.max([Comm_pi_lambda_A, Comm_pi_lambda_B, Comm_pi_lambda_C])

	# Compute the maximum computational latency (as observed in the Pi, not Lambda)
	Compu_pi_A = item_A['Compu_pi']
	Compu_pi_B = item_B['Compu_pi']
	Compu_pi_C = item_C['Compu_pi']
	Compu_pi = np.max([Compu_pi_A, Compu_pi_B, Compu_pi_C])

	def prox_simplex(y):
		# projection onto simplex
		n = len(y)
		val = -np.sort(-y)
		suppt_v = np.cumsum(val) - np.arange(1, n+1, 1) * val
		k_act = np.sum(suppt_v < 1)
		lam = (np.sum(val[0:k_act]) - 1.0) / k_act
		x = np.maximum(y-lam, 0.0)
		return x

	def combine(y, X, betam):
		K = betam.shape[1]
		w = np.ones((K,)) / K
		maxit = 1000
		tol = 1e-3
		Xb = np.dot(X, betam)
		step = 1.0 / np.max(np.linalg.svd(Xb, full_matrices=0, compute_uv=0)) ** 2

		for it in range(maxit):
			prev_w = np.copy(w)
			res = y - np.dot(np.matrix(Xb), np.matrix(w).T)
			grad = -np.dot(np.matrix(Xb).T, np.matrix(res))
			w -= step * np.squeeze(np.asarray(grad.T))
			w = prox_simplex(w)
			if np.linalg.norm(w - prev_w) / (1e-20 + np.linalg.norm(prev_w)) < tol:
				break

		return w

	w = combine(y, X, betam)
	w_temp = [decimal.Decimal(str(w[i]))for i in range(collectornum)]

	wb = np.dot(np.matrix(betam), np.matrix(w).T)
	Predict_y = np.dot(np.matrix(X), wb)
	Predict_y_array = np.squeeze(np.asarray(Predict_y))

	# Mean Square Error
	MSE = np.sqrt(np.sum((y-np.squeeze(np.asarray(Predict_y))) ** 2)) / datanum
	MSE_temp = decimal.Decimal(str(MSE))

	# Prepare data for DB so that DemoPlot.py can access it
	Predict_y_array = Predict_y_array.tolist()
	y = y.tolist()
	for i in range(len(Predict_y_array)):
		y[i] = decimal.Decimal(str(y[i][0]))
		Predict_y_array[i] = decimal.Decimal(str(Predict_y_array[i]))

	tEnd = time.time()
	Lambda_ExecTime = tEnd - tStart
	tEnd_temp = decimal.Decimal(str(tEnd))
	Lambda_ExecTime_temp = decimal.Decimal(str(Lambda_ExecTime))

	table = dynamo.Table('weightresult')
	resultData = {
		'environment' : 'roomA',
		'sensor': 'sensorA&B&C',
		'w_1' : w_temp[0],
		'w_2' : w_temp[1],
		'Prediction' : Predict_y_array,
		'Real_Data' : y,
		'Error' : MSE_temp,
		'Lambda_ExecTime' : Lambda_ExecTime_temp,
		'Time': tEnd_temp,
		'Comm_pi_pi': Comm_pi_pi,
		'Comm_pi_lambda': Comm_pi_lambda,
		'Compu_pi': Compu_pi,
		'data_bytes_features' : decimal.Decimal(str(dataBytesFeatures)),
		'data_bytes_entire' : decimal.Decimal(str(data_bytes_entire))
	}
	item = table.put_item(Item = resultData)

	# Remove data that we don't want to track over time
	resultData.pop('environment', None)
	resultData.pop('sensor', None)
	resultData.pop('Prediction', None)
	resultData.pop('Real_Data', None)

	# Log the data to DynamoDB
	data_labels = []
	new_data = []
	for key in resultData.keys():
		data_labels.append(key)
		new_data.append(resultData[key])

	record = table.get_item(Key = {'environment' : 'roomA', 'sensor' : 'expResults'})['Item']
	record['data_labels'] = data_labels
	results = record['results']
	results.append(new_data)
	item = table.put_item(Item = record)
