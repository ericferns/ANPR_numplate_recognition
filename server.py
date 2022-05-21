
import socket
import pandas as pd 
import time
from datetime import datetime

tdata = (b'True')
fdata = (b'False')

#t = time.localtime()
#timex = time.strftime('%b-%d-%Y_%H%M', t)
timex = datetime.now().strftime("%d_%m_%Y-%I_%M_%S_%p")

# create TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# retrieve locoicalcal hostname
host = 'vvf.co.in'

# get fully qualified hostname
#local_fqdn = socket.getfqdn()

port = 8001
# get the according IP address
#ip_address = host

# output hostname, domain name and IP address
#print ("working on (%s) with %s" % (local_fqdn, ip_address))

# bind the socket to the port 23456
#server_address = ('192.168.1.101', 12345)
#print ('starting up on %s port %s' % server_address)
sock.bind((host, port))

# listen for incoming connections (server mode) with one connection at a time
sock.listen(5)

while True:
    # wait for a connection
    print ('waiting for a connection')
    #print (client_address)
    connection, client_address = sock.accept()
    print (client_address)
    try:
        # show who connected to us
        print ('connection from', client_address)

        # receive the data in small chunks and print it
        while True:
            data = connection.recv(1024)
            if data is not None:
                # output received data
                #print ("NumberPlate: %s" % data)
                current_license = data.decode("utf-8")
                #print('current_license', current_license)
                vveh_letter = []
                vvehexists = ''
                str_plt = ''
                alpha = pd.read_csv('./alpha.csv')
                for V in current_license:
                    #print('V', V)
                    vletter_exist = V in alpha.values
                 #   print('vletter', vletter_exist)
                    if vletter_exist:
                        vveh_letter.append(V)
                        #print('vveh_letter', vveh_letter)
                    str_plt = ''.join(vveh_letter)
                    #print('str_plt', str_plt)
                print("Number Plate string: %s" % str_plt)		
                database = pd.read_csv('pltnumbers.csv')
                validity = str_plt in database.values
                wdata = str(data) + ',' + str(time) + "\n"# + ',' + str(date)
                with open("./archive/all/all.txt", "a") as outfile:
                    outfile.write(wdata)
                    outfile.close()
                if validity is True:
                    validdata = database[database['vehno'] == data]
                    with open("./archive/registered/registered.txt", "a") as outfiletrue:
                        outfiletrue.write(wdata)
                        outfiletrue.close()
                    print('validdata', validdata.vehowner)
                    connection.sendall(tdata)
                else:
                    outfilefalse = open("./archive/unregistered/unregistered.txt", "a")  # append mode 
                    outfilefalse.write(wdata) 
                    outfile.close()
                    connection.sendall(fdata)
            else:
                # no more data -- quit the loop
                print ("no more vehicles.")
                break
    finally:
        # Clean up the connection
        connection.close()

