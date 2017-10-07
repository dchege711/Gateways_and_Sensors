'''
Handles all the operations involving Bluetooth data transfer.

'''
#_______________________________________________________________________________

import bluetooth
import pickle
import cPickle
import time
import LEDManager as LED
from sense_hat import SenseHat

#_______________________________________________________________________________

# Obtain the bluetooth addresses by running `$ hciconfig` in the terminal
gatewayBRAddresses = {
    'A' : 'B8:27:EB:8A:43:B1',
    'B' : 'B8:27:EB:1D:9D:BF',
    'C' : 'B8:27:EB:57:29:09'
}

sensorBRAddresses = {
    'A' : 'B8:27:EB:C3:A3:C5',
    'B' : 'B8:27:EB:E7:5E:3C',
    'C' : 'B8:27:EB:6C:16:BA'
}

sense = SenseHat()

#_______________________________________________________________________________

def listenOnBluetooth(channelNumber):
    '''
    Listens to incoming data on the Bluetooth Interface

    Param(s):
    (int)       Port that we going to listen to

    Return(s)
    (pickle)    ???

    '''
    allowableUnacceptedConns = 1 # The # of unaccepted connection before refusing new connections
    bufferSize = 1 # Receive up to this number of buffersize bytes from the socket

    # Setup the Bluetooth connection
    sense.set_pixels(LED.arrowReceive('orange', 'red'))
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", channelNumber))
    server_sock.listen(allowableUnacceptedConns)

    # startTime = time.time()
    total_data = []

    # Listen for incoming data, while watching for the keyboard interrupt
    try:
        sense.set_pixels(LED.arrowReceive('orange', 'blue'))
        # The received address is a (host, channel) tuple
        client_sock, address = server_sock.accept()
        # startTime = time.time()

        while True:
            startTime = time.time()
            data_1 = client_sock.recv(bufferSize)
            # We need a break statement because when no data is available,
            # recv() blocks until at least one byte is available
            if len(data_1) == 0:
                break
            # Append the received data to the helper variable
            total_data.append(data_1)

        # Should we stop timing at this point?
        # endTime = time.time()

    except IOError:
        sense.set_pixels(LED.arrowReceive('orange', 'magenta'))
        # print("Ran into IOError")
        pass    # Sincere apologies to all who told me passing is poor practice

    except KeyboardInterrupt:
        sense.set_pixels(LED.arrowReceive('orange', 'magenta'))
        bluetooth.stop_advertising(server_sock)
        # sys.exit()    Why do we need an exit before we're actually done?

    # Log the results of the bluetooth data to the console
    sense.set_pixels(LED.arrowReceive('orange', 'green'))
    endTime = time.time()
    btTime = endTime - startTime

    print("Bluetooth Transmission Time :", btTime)

    # Close the bluetooth connection
    client_sock.close()
    server_sock.close()

    return btTime, pickle.loads(''.join(total_data))

#_______________________________________________________________________________

def sendDataByBluetooth(data, gatewayLetter, channelNumber):
    '''
    Param(s):
        (String)    Destination Address
        (int)       Destination Channel

    Sends data over bluetooth to the designated address and channel.
    Run "$ hciconfig dev" on the Pi to identify the address

    '''
    bd_addr = gatewayBRAddresses[gatewayLetter]

    # Establish the bluetooth connection
    sense.set_pixels(LED.arrowSend('blue', 'red'))

    startTime = time.time()
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((bd_addr, channelNumber))

    # Send the data
    sense.set_pixels(LED.arrowSend('blue', 'blue'))
    dataToSend = cPickle.dumps(data)
    intendedBytes = len(dataToSend)
    bytesSent = sock.send(dataToSend)

    sense.set_pixels(LED.arrowSend('blue', 'green'))
    sock.close()

    endTime = time.time()
    btTime = endTime - startTime
    print("Sensor : Sent", bytesSent, "/", intendedBytes, "bytes over bluetooth in", btTime, "seconds")
    return btTime

#_______________________________________________________________________________
