***Python*** (you need to change all the table names in all of the following .py)
1.rfcomm-client.py : put this in your sensor Pi
2.rfcomm-server.py : put this in your gateway Pi

1.You can try to design the lambda python code (dynamo.py), and delete the old one in the dynamo.zip, include new one into dynamo.zip,and then upload to Amazon Lambda.
2.Run Demo.py : it will show you the table of result
3.Run trigger.py : you can see a number on command line, if the number is 3, that means the data from 3 getway Pi are all uploaded to dynamodb, on the other word, it's time to trigger lambda.
4.Run button.py : you can see a button in a window, and enter your sample size, and then press "Start"

***pdf***
1.Pi system user guide.pdf : you can follow the step in this pdf
2.Exact interaction : this pdf shows you the exact interaction between tables, Pis, Lambda, and laptop.
