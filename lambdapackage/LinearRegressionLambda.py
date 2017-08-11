'''
A linear regression model that runs on AWS Lambda

AWS needs a zip file because it doesn't have numpy (so I can't use the console editor)
Make sure the zip file name, .py name and the handler name on Lambda coincide.

'''

#_______________________________________________________________________________

import json
import boto3
import numpy as np
import decimal
from decimal import *
import time
print('Loading function')

#_______________________________________________________________________________

def lambda_handler(event, context):
	tStart = time.time()
	dynamo = boto3.resource('dynamodb')
	table_S = dynamo.Table('SampleSize')
	db_response_S = table_S.scan()
	item_S = tuple(db_response_S['Items'])
	datanum = int(item_S[0]['sampleSize'])

	featurenum = 3
	collectornum = 2
	#w_temp = np.zeros((1,collectornum),dtype = decimal.Decimal)
	X = np.zeros((datanum,featurenum))
	y = np.zeros((datanum,1))
	betam = np.zeros((featurenum,collectornum))

	table_A = dynamo.Table('sensingdata_A')
	table_B = dynamo.Table('sensingdata_B')
	table_C = dynamo.Table('sensingdata_C')

	db_response_A = table_A.scan()
	item_A = tuple(db_response_A['Items'])


	betam[0][0] = item_A[0]['feature_A']
	betam[1][0] = item_A[0]['feature_B']
	betam[2][0] = item_A[0]['feature_C']


	db_response_B = table_B.scan()
	item_B = tuple(db_response_B['Items'])


	betam[0][1] = item_B[0]['feature_A']
	betam[1][1] = item_B[0]['feature_B']
	betam[2][1] = item_B[0]['feature_C']

	db_response_C = table_C.scan()

	item_C = tuple(db_response_C['Items'])
	for i in range(datanum):
		X[i][0] = item_C[i]['X_1']
		X[i][1] = item_C[i]['X_2']
		X[i][2] = item_C[i]['X_3']
		y[i][0] = item_C[i]['Y']

	data_bytes = item_C[1000]['data_bytes']

	#print X
	#print y
	#print data_bytes

	table_LC = dynamo.Table('latency_C')
	db_response_LC = table_LC.scan()
	item_LC = tuple(db_response_LC['Items'])
	Comm_pi_pi_A = item_A[0]['Comm_pi_pi']
	Comm_pi_pi_B = item_B[0]['Comm_pi_pi']
	Comm_pi_pi_C = item_LC[0]['Comm_pi_pi']
	Comm_pi_lambda_A = item_A[0]['Comm_pi_lambda']
	Comm_pi_lambda_B = item_B[0]['Comm_pi_lambda']
	Comm_pi_lambda_C = item_LC[0]['Comm_pi_lambda']
	Compu_pi_A = item_A[0]['Compu_pi']
	Compu_pi_B = item_B[0]['Compu_pi']
	Compu_pi_C = item_LC[0]['ExecTime']
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
	Predict_y_temp = decimal.Decimal(str(Predict_y_array[199]))

	MSE = np.sqrt(np.sum((y-np.squeeze(np.asarray(Predict_y)))**2))/datanum
	MSE_temp = decimal.Decimal(str(MSE))
	tEnd = time.time()
	Lambda_ExecTime = tEnd - tStart
	tEnd_temp = decimal.Decimal(str(tEnd))
	Lambda_ExecTime_temp = decimal.Decimal(str(Lambda_ExecTime))
	table = dynamo.Table('weightresult')
	#print Predict_y

	item = table.put_item(
		Item = {
			'environment' : 'roomA',
			'sensor': 'sensorA&B&C',
			'w_1' : w_temp[0],
			'w_2' : w_temp[1],
			'Prediction' : Predict_y_temp,
			#'Real_Result' : y[199],
			'Error' : MSE_temp,
			'Lambda_ExecTime' : Lambda_ExecTime_temp,
			'Time': tEnd_temp,
			'Comm_pi_pi': Comm_pi_pi,
			'Comm_pi_lambda': Comm_pi_lambda,
			'Compu_pi': Compu_pi,
			}
	)


	##Bytes of data##
	#def utf8len(s):
	#	return len(s.encode('utf-8'))

	#data_bytes = utf8len(str(w_temp[0]))+utf8len(str(w_temp[1]))+utf8len(str(Predict_y_temp))+utf8len(str(y))+utf8len(str(MSE_temp))+utf8len(str(Lambda_ExecTime_temp))
	print datanum
	#return betam
	#print betam
	#print w
	#print Lambda_ExecTime
	#print data_bytes
	#print MSE
