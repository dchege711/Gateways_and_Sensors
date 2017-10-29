'''
A linear regression model that runs on AWS Lambda

AWS needs a zip file because it doesn't have numpy (so I can't use the console editor)
Make sure the zip file name, .py name and the handler name on Lambda coincide.

@ Original Author :	Liang Zheng
@ Modified by	  : Chege Gitau

'''

#_______________________________________________________________________________

import numpy as np
import decimal
from decimal import *
import time
import matplotlib.pyplot as plt
from collections import namedtuple

from DynamoDBUtility import Table

print('Loading function')

def gradientDescent(targetMatrix, designMatrix, featurenum, numDataPoints):
    """
    Runs the gradient descent algorithm.

    Param(s):
        (numpy array)   The target matrix
        (numpy array)   The design matrix

    Returns a numpy array of features that approximate the mapping
    """

    count = 0
    w_old = np.zeros((featurenum, 1))
    w_new = np.zeros((featurenum, 1))
    E_old = 0
    E_new = 0
    delta_E = np.zeros((numDataPoints, featurenum))
    learning_rate = 0.001
    # tolerance = 1e-5

    while True:
        w_old = w_new

        for i in range(numDataPoints):
            delta_E[i,:] = delta_E[i,:] + (targetMatrix[i][0] - np.dot(np.matrix(designMatrix[i,:]), np.matrix(w_old))) * designMatrix[i,:]

        w_new = w_old + learning_rate * np.matrix(delta_E[i, :] / (numDataPoints * 2)).T
        E_old = E_new

        for i in range(numDataPoints):
            E_new = E_new + (targetMatrix[i][0] - np.dot(np.matrix(designMatrix[i, :]), np.matrix(w_new))) ** 2
            E_new = E_new / 2

        if E_new > E_old:
            learning_rate = learning_rate / 2

        count = count + 1
        # print("E_new", E_new, "E_old", E_old)
        if count % 20 == 0:
            # print(" ".join[count, "iterations so far..."])
            print(str(count), " iterations so far...")

        # Comparing E_new == E_old is tricky because of precision.
        if np.isclose(E_new, E_old)[0]:
            #print(" ".join(["Escaped loop after", count, "iterations."]))
            print("Escaped loop after", str(count), "iterations.")
            break

    # Return feature_A, feature_B, feature_C
    return w_new[0][0], w_new[1][0], w_new[2][0]

#_______________________________________________________________________________

def convertToNumpyArrays(aggregatedData, featurenum, datanum):
	"""
	Convert raw data into numpy arrays for further computation.

	Param(s):

		aggregatedData (list)
		The data that will be copied into a numpy array.

		featurenum (int)
		The number of features being used in the regression model.

	Return(s):
		A numpy 1D matrix containing the labelling feature.
		A numpy matrix containing all the descriptive features.

	"""

	designMatrix = np.zeros((datanum,featurenum))
	targetMatrix = np.zeros((datanum,1))

	for i in range(datanum):
		designMatrix[i][0] = aggregatedData[i]['X_1']
		designMatrix[i][1] = aggregatedData[i]['X_2']
		designMatrix[i][2] = aggregatedData[i]['X_3']
		targetMatrix[i][0] = aggregatedData[i]['Y']

	return targetMatrix, designMatrix

def calculate_features(aggregatedData, featurenum):
	datanum = len(aggregatedData)
	targetMatrix, designMatrix = convertToNumpyArrays(aggregatedData, featurenum, datanum)
	features = gradientDescent(targetMatrix, designMatrix, featurenum, datanum)

	return features

def insert_features(feature_values, featurenum, betam, index):
	for i in range(featurenum):
		betam[i][index] = feature_values[i]
	return betam

def read_gateway_data(gateway_letter, call_fetch_test_data=False):

	# All of the tables share a common format
	table_name = "".join(["sensingdata_", gateway_letter])
	sensor_name = "".join(["sensor", gateway_letter])
	table = Table(table_name)
	item = table.getItem({
		"forum"		: "roomA",
		"subject"	: sensor_name
	})
	fog_or_cloud = None

	try:
		features = item["feature_A"], item["feature_B"], item["feature_C"]
		print("Collected features from table", gateway_letter)
		fog_or_cloud = "fog (edge + cloud)"
		X, y, datanum = None, None, None
	except KeyError:
		aggregatedData = item["aggregated_data"]
		datanum = len(aggregatedData)
		# Because one of them is a target feature...
		featurenum = len(aggregatedData[0]) - 1	
		fog_or_cloud = "all_cloud"

		if call_fetch_test_data:
			X, y = fetch_test_data(aggregatedData, featurenum)
			features = None
			print("Collected test data from table", gateway_letter)

		else:
			X, y = None, None
			features = calculate_features(aggregatedData, featurenum)
			print("Calculated summarized features for table", gateway_letter)


	# Return the data obtained
	gateway_results = namedtuple('gateway_results', 
		[
			'X', 'y', 'features', 'data_bytes', 'Compu_pi', 'datanum', 'fog_or_cloud',
			'number_of_sensors', 'Comm_pi_pi', 'Comm_pi_lambda', 'timeStamp'
	])

	results = gateway_results(
		X,
		y,
		features,
		item['data_bytes'],
		item['Compu_pi'],
		datanum,
		fog_or_cloud,
		item['number_of_sensors'],
		item['Comm_pi_pi'],
		item['Comm_pi_lambda'],
		item['timeStamp']
	)

	return results

def fetch_test_data(aggregatedData, featurenum):
	datanum = len(aggregatedData)
	# Some of the gateways may be used as sources of test data
	# that helps us gauge the accuracy of our model
	X = np.zeros((datanum, featurenum))
	y = np.zeros((datanum, 1))
	# Think of a cleaner way of doing this. Are we guaranteed that
	# X_number are descriptive features and Y is the target such that
	# we can sort the keys and remove the last item?
	data_item_keys = list(aggregatedData[0].keys())
	data_item_keys.sort()

	for i in range(datanum):
		for j in range(featurenum):
			X[i][j] = aggregatedData[i][data_item_keys[j]]
		# In this case, featurenum = index of the target feature
		# We're assuming only one target feature
		y[i][0] = aggregatedData[i][data_item_keys[featurenum]]

	return X, y

def lambda_handler(event, context):
	# Fetch the DynamoDB resource
	tStart = time.time()

	# How to automatically set this up?
	featurenum = 3
	collectornum = 2
	betam = np.zeros((featurenum,collectornum))
	dataBytesFeatures = 0
	numSensors = 0

	# Fetch the data from Gateway A's table
	item_A = read_gateway_data('A')
	betam = insert_features(item_A.features, featurenum, betam, 0)
	dataBytesFeatures += item_A.data_bytes
	numSensors += item_A.number_of_sensors
	fog_or_cloud = item_A.fog_or_cloud

	# Fetch the data from Gateway B's table
	item_B = read_gateway_data('B')
	betam = insert_features(item_B.features, featurenum, betam, 0)
	dataBytesFeatures += item_B.data_bytes
	numSensors += item_B.number_of_sensors

	# Fetch the aggregated data from Gateway C
	item_C = read_gateway_data('C', call_fetch_test_data=True)
	numSensors += item_C.number_of_sensors
	data_bytes = item_C.data_bytes
	size_of_one_reading = 32
	readings_per_sensor = str(data_bytes / size_of_one_reading)
	datanum = item_C.datanum	# Whichever item has test data has datanum
	X = item_C.X
	y = item_C.y

	# Compute the maximum bluetooth latency
	Comm_pi_pi = np.max([
		item_A.Comm_pi_pi, 
		item_B.Comm_pi_pi, 
		item_C.Comm_pi_pi
	])

	# Compute the maximum upload latency
	Comm_pi_lambda = np.max([
		item_A.Comm_pi_lambda,
		item_B.Comm_pi_lambda,
		item_C.Comm_pi_lambda
	])

	# Compute the maximum computational latency 
	# * As observed in the Pi, not on AWS Lambda
	Compu_pi = np.max([
		item_A.Compu_pi,
		item_B.Compu_pi,
		item_C.Compu_pi
	])

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
	w_temp = [decimal.Decimal(str(w[i])) for i in range(collectornum)]

	wb = np.dot(np.matrix(betam), np.matrix(w).T)
	Predict_y = np.dot(np.matrix(X), wb)
	Predict_y_array = np.squeeze(np.asarray(Predict_y))

	MSE = np.sqrt(np.sum((y-np.squeeze(np.asarray(Predict_y))) ** 2)) / datanum
	MSE_temp = decimal.Decimal(str(MSE))
	tEnd = time.time()
	Lambda_ExecTime = tEnd - tStart
	tEnd_temp = decimal.Decimal(str(tEnd))
	Lambda_ExecTime_temp = decimal.Decimal(str(Lambda_ExecTime))

	Predict_y_array = Predict_y_array.tolist()
	y = y.tolist()
	for i in range(len(Predict_y_array)):
		y[i] = decimal.Decimal(str(y[i][0]))
		Predict_y_array[i] = decimal.Decimal(str(Predict_y_array[i]))


	table = Table('weightresult')
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
		'readings_per_sensor': readings_per_sensor,
		'fog_or_cloud': fog_or_cloud,
		'data_bytes_features' : decimal.Decimal(str(dataBytesFeatures)),
		'data_bytes_entire' : decimal.Decimal(str(data_bytes)),
		'number_of_sensors':decimal.Decimal(str(numSensors))
	}
	item = table.addItem(resultData)

	# Record this run
	resultData.pop('environment', None)
	resultData.pop('sensor', None)
	resultData.pop('Prediction', None)
	resultData.pop('Real_Data', None)
	resultData['gateway_A_subject'] = str(item_A.timeStamp)
	resultData['gateway_B_subject'] = str(item_B.timeStamp)
	resultData['gateway_C_subject'] = str(item_C.timeStamp)

	for key in resultData.keys():
		print(key, "\t", resultData[key])
	
	record = table.getItem({'environment' : 'roomA', 'sensor' : 'cloud_vs_fog'})
	results = record['results']
	results.append(resultData)
	# item = table.addItem(record)

lambda_handler(35, 46)
