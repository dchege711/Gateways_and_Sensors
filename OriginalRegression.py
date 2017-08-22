import json
import boto3
import numpy as np
import decimal
from decimal import *
import time
print('Loading function')
from DynamoDBUtility import Table

def lambda_handler(event, context):
	tStart = time.time()
	table_S = Table('SampleSize')
	query = {'subject' : 'PC1', 'forum' : '1'}
	item_S = table_S.getItem(query)
	datanum = int(item_S['sampleSize'])

	featurenum = 3
	collectornum = 2
	#w_temp = np.zeros((1,collectornum),dtype = decimal.Decimal)
	X = np.zeros((datanum,featurenum))
	y = np.zeros((datanum,1))
	betam = np.zeros((featurenum,collectornum))

	table_A = Table('sensingdata_A')
	table_B = Table('sensingdata_B')
	table_C = Table('sensingdata_C')

	query = {'subject' : 'sensorA', 'forum' : 'roomA'}
	item_A = table_A.getItem(query)


	betam[0][0] = item_A['feature_A']
	betam[1][0] = item_A['feature_B']
	betam[2][0] = item_A['feature_C']


	query = {'subject' : 'sensorB', 'forum' : 'roomA'}
	item_B = table_B.getItem(query)


	betam[0][1] = item_B['feature_A']
	betam[1][1] = item_B['feature_B']
	betam[2][1] = item_B['feature_C']

	query = {'subject' : 'sensorC', 'forum' : 'roomA'}
	item_C = table_C.getItem(query)
	measuredData = item_C['aggregated_data']

	for i in range(datanum):
		X[i][0] = measuredData[i]['X_1']
		X[i][1] = measuredData[i]['X_2']
		X[i][2] = measuredData[i]['X_3']
		y[i][0] = measuredData[i]['Y']

	data_bytes = item_C['data_bytes']

	#print X
	#print y
	#print data_bytes

	# table_LC = dynamo.Table('latency_C')
	# db_response_LC = table_LC.scan()
	# item_LC = tuple(db_response_LC['Items'])
	Comm_pi_pi_A = item_A['Comm_pi_pi']
	Comm_pi_pi_B = item_B['Comm_pi_pi']
	Comm_pi_pi_C = item_C['Comm_pi_pi']
	Comm_pi_lambda_A = item_A['Comm_pi_lambda']
	Comm_pi_lambda_B = item_B['Comm_pi_lambda']
	Comm_pi_lambda_C = item_C['Comm_pi_lambda']
	Compu_pi_A = item_A['Compu_pi']
	Compu_pi_B = item_B['Compu_pi']
	Compu_pi_C = item_C['Compu_pi']
	Comm_pi_pi = np.max([Comm_pi_pi_A,Comm_pi_pi_B,Comm_pi_pi_C])
	Comm_pi_lambda = np.max([Comm_pi_lambda_A,Comm_pi_lambda_B,Comm_pi_lambda_C])
	Compu_pi = np.max([Compu_pi_A,Compu_pi_B,Compu_pi_C])


	'''
	X = [150.005827158,1014.56323242,42.7386322021]
	y = 31.2729568481
	betam = [[0.00352444991866,0.00663154254902],[0.0238683682846,0.0448808648642],[0.000894580604741,0.00179057056997]]
	'''

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
		#print Xb
		step = 1.0 / np.max(np.linalg.svd(Xb, full_matrices=0, compute_uv=0)) ** 2

		for it in range(maxit):
			prev_w = np.copy(w)
			#print w
			res = y - np.dot(np.matrix(Xb),np.matrix(w).T)
			#print res
			grad = -np.dot(np.matrix(Xb).T,np.matrix(res))
			#print grad
			#print step
			w -= step * np.squeeze(np.asarray(grad.T))
			w = prox_simplex(w)
			#print(w)
			if np.linalg.norm(w - prev_w) / (1e-20 + np.linalg.norm(prev_w)) < tol:
				break

		return w

	w = combine(y,X,betam)
	w_temp = [decimal.Decimal(str(w[i]))for i in range(collectornum)]
	#print type(w_temp[0])
	#print (w_temp[0])

	wb = np.dot(np.matrix(betam),np.matrix(w).T)
	Predict_y = np.dot(np.matrix(X),wb)
	Predict_y_array = np.squeeze(np.asarray(Predict_y))
	Predict_y_temp = str(Predict_y_array[199])
	# print("Predict_y ==> ", len(Predict_y), "Predict_y_array ==> ", len(Predict_y_array))

	MSE = np.sqrt(np.sum((y-np.squeeze(np.asarray(Predict_y)))**2))/datanum
	MSE_temp = decimal.Decimal(str(MSE))
	tEnd = time.time()
	Lambda_ExecTime = tEnd - tStart
	tEnd_temp = decimal.Decimal(str(tEnd))
	Lambda_ExecTime_temp = decimal.Decimal(str(Lambda_ExecTime))

	# table = Table('weightresult')
	# print Predict_y

	resultItem = {
		'environment' : 'roomA',
		'sensor': 'sensorA&B&C',
		'w_1' : w_temp[0],
		'w_2' : w_temp[1],
		'Prediction' : Predict_y_temp,
		'Real_Result' : str(y[199]),
		'Error' : MSE_temp,
		'Lambda_ExecTime' : Lambda_ExecTime_temp,
		'Time': tEnd_temp,
		'Comm_pi_pi': Comm_pi_pi,
		'Comm_pi_lambda': Comm_pi_lambda,
		'Compu_pi': Compu_pi
	}
	# item = table.addItem(resultItem)

	for key in resultItem.keys():
		print('{:20}'.format(key), resultItem[key])

lambda_handler(67, 34)
