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

def insertFeatures(betam, aggregatedData, collectorIndex, featurenum):
	datanum = len(aggregatedData)
	targetMatrix, designMatrix = convertToNumpyArrays(aggregatedData, featurenum, datanum)
	feature_A, feature_B, feature_C = gradientDescent(targetMatrix, designMatrix, featurenum, datanum)

	betam[0][collectorIndex] = feature_A
	betam[1][collectorIndex] = feature_B
	betam[2][collectorIndex] = feature_C

	return betam


def lambda_handler(event, context):
	# Fetch the DynamoDB resource
	tStart = time.time()

	# Change: Getting the number of samples from the 'SampleSize' table is tricky
	# When we'll have multiple Pi's, keeping track of this number will be buggy
	# For this reason, I'm setting the value of 'datanum' to the number of items
	# that we're going to get from the table containing the aggregated sensor data

	# Initialize helper variables
	featurenum = 3
	collectornum = 2
	betam = np.zeros((featurenum,collectornum))
	dataBytesFeatures = 0
	numSensors = 0

	# Fetch the data from Gateway A's table
	table_A = Table('sensingdata_A')
	itemKey = {'forum' : 'roomA', 'subject' : 'sensorA'}
	item_A = table_A.getItem(itemKey)
	aggregatedData_A = item_A['aggregated_data']
	betam = insertFeatures(betam, aggregatedData_A, 0, featurenum)
	dataBytesFeatures += item_A['data_bytes']
	numSensors += item_A['number_of_sensors']

	# Fetch the data from Gateway B's table
	table_B = Table('sensingdata_B')
	itemKey = {'forum' : 'roomA', 'subject' : 'sensorB'}
	item_B = table_B.getItem(itemKey)
	aggregatedData_B = item_B['aggregated_data']
	betam = insertFeatures(betam, aggregatedData_B, 1, featurenum)
	dataBytesFeatures += item_B['data_bytes']
	numSensors += item_B['number_of_sensors']

	# Fetch the aggregated data from Gateway C
	table_C = Table('sensingdata_C')
	itemKey = {'forum' : 'roomA', 'subject' : 'sensorC'}
	item_C = table_C.getItem(itemKey)
	aggregatedData_C = item_C['aggregated_data']
	numSensors += item_C['number_of_sensors']
	data_bytes = item_C['data_bytes']
	datanum = len(aggregatedData_C)
	X = np.zeros((datanum,featurenum))
	y = np.zeros((datanum,1))

	for i in range(datanum):
		X[i][0] = aggregatedData_C[i]['X_1']
		X[i][1] = aggregatedData_C[i]['X_2']
		X[i][2] = aggregatedData_C[i]['X_3']
		y[i][0] = aggregatedData_C[i]['Y']

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
	Compu_pi = np.max([Compu_pi_A,Compu_pi_B,Compu_pi_C])

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
	resultData['gateway_A'] = aggregatedData_A
	resultData['gateway_B'] = aggregatedData_B
	resultData['gateway_C'] = aggregatedData_C
	
	record = table.getItem({'environment' : 'roomA', 'sensor' : 'all_cloud_results'})
	results = record['results']
	results.append(resultData)
	item = table.addItem(record)


lambda_handler(35, 46)
