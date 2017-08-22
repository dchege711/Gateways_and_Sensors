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
    'A' : 'B8:27:EB:3F:84:11',
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

def listenOnBluetooth(port):
    '''
    Listens to incoming data on the Bluetooth Interface

    Param(s):
    (int)       Port that we going to listen to

    Return(s)
    (pickle)    ???

    '''
    # Setup the Bluetooth connection
    sense.set_pixels(LED.arrowReceive('orange', 'red'))
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(port)

    # startTime = time.time()
    total_data = []

    # Listen for incoming data, while watching for the keyboard interrupt
    try:
        sense.set_pixels(LED.arrowReceive('orange', 'blue'))
        client_sock, address = server_sock.accept()
        # print("Accepted connection from", address)
        startTime = time.time()

        while True:
            data_1 = client_sock.recv(port)
            # If there's no more data to receive, escape the loop
            if len(data_1) == 0:
                break
            # Else append the received data to the helper variable
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

def sendDataByBluetooth(data, gatewayLetter, port):
    '''
    Param(s):
        (String)    Destination Address
        (int)       Destination Port

    Sends data over bluetooth to the designated address and port.
    Run "$ hciconfig dev" on the Pi to identify the address

    '''
    bd_addr = gatewayBRAddresses[gatewayLetter]

    # Establish the bluetooth connection
    sense.set_pixels(LED.arrowSend('blue', 'red'))
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((bd_addr, port))

    # Send the data
    sense.set_pixels(LED.arrowSend('blue', 'blue'))
    startTime = time.time()
    sock.send(cPickle.dumps(data))
    endTime = time.time()
    btTime = endTime - startTime
    sense.set_pixels(LED.arrowSend('blue', 'green'))
    sock.close()
    print("Sensor : Sent data over bluetooth in", btTime, "seconds")
    return btTime

#_______________________________________________________________________________
