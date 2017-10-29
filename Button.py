'''
Creates a GUI interface for specifying the number of samples to DynamoDB.
Once a number is uploaded to DynamoDB, the Pi's notice the addition and start
running the experiment.

@ Original Author   : Edward Chang
@ Modified by       : Chege Gitau

'''
#_______________________________________________________________________________

# tkinter was was previously named Tkinter in python 2
import sys
version = sys.version_info.major
print(version)
if version == 2:
	import Tkinter as tk
elif version == 3:
	import tkinter as tk
else:
	raise ImportError("This script needs either Python 2 or Python 3")
	
import time
import os
from decimal import Decimal

from DynamoDBUtility import Table

#_______________________________________________________________________________

# Set up the Graphic User Interface
window = tk.Tk()
window.title('Input your sample amount!')
window.geometry('200x200')
label=tk.Label(window, text="Enter Sample Size")
label.pack()
e = tk.Entry(window, show=None)
e.pack()

#_______________________________________________________________________________

table = Table('SampleSize')

def set_sample_size(sample_size=None, table_letter=None):
	'''
	Listens to the GUI for the sample size of the experiment.
	Uploads this number to DynamoDB so that the Pi's can access it.

	The sample_size param allows a script (e.g. GatewayPi.py) to 
	simulate the press of the button.

	Returns the time stamp so that we can prevent infinite loops 
	by the gateway.

	'''
	# item['sampleSize'] = e.get() # e.get is the number you entered in the window

	# If none, then it came from GUI and this value should be passed
	# to all the gateways
	if sample_size is None:
		sample_size = Decimal(e.get())
		tStart = update_table('A', sample_size)
		tStart = update_table('B', sample_size)
		tStart = update_table('B', sample_size)

	else:
		tStart = update_table(table_letter, sample_size)

	return tStart

def update_table(table_letter, sample_size):
	tStart = time.time()
	subject_val = "".join(["gateway_", table_letter])
	item = table.getItem({
		'forum'		: '1',
		'subject'	: subject_val
	})
	item['timeStamp'] = Decimal(tStart)
	table.addItem(item)
	return tStart


#_______________________________________________________________________________

# Display the submission button
b1 = tk.Button(window, text = 'Start', width = 15, height = 2, command = set_sample_size)
b1.pack()
window.mainloop()

#_______________________________________________________________________________
