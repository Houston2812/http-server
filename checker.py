from socket import *
import sys
import random
import os
import time

if len(sys.argv) < 7:
    sys.stderr.write('Usage: %s <ip> <port> <#trials>\
            <#writes and reads per trial>\
            <max # bytes to write at a time> <#connections> \n' % (sys.argv[0]))
    sys.exit(1)

serverHost = gethostbyname(sys.argv[1])
serverPort = int(sys.argv[2])
numTrials = int(sys.argv[3])
numWritesReads = int(sys.argv[4])
numBytes = int(sys.argv[5])
numConnections = int(sys.argv[6])

socketList = []

RECV_TOTAL_TIMEOUT = 0.1
RECV_EACH_TIMEOUT = 0.01


for i in range(numConnections):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((serverHost, serverPort))
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    socketList.append(s)


for i in range(numTrials):
    socketSubset = []
    datas = []
    lens = []
    socketSubset = random.sample(socketList, numConnections)
    for j in range(numWritesReads):
        random_string = b'HEAD www/test_visual/index.html HTTP/1.1\r\nHost: 0.0.0.0\r\nConnection:Keep-Alive\r\nContent-Type: text/html\r\n\r\n\r\n'
        random_len = len(random_string)

        lens.append(random_len)
        datas.append(random_string)
        time.sleep(0.01)
        socketSubset[j].send(random_string)

    for j in range(numWritesReads):

        try:
            data = socketSubset[j].recv(lens[j])
        except Exception as e:
            print(f"J: {j}; Socket: {socketSubset[j]}")
        start_time = time.time()
        while True:
            if len(data) == lens[j]:
                break
            socketSubset[j].settimeout(RECV_EACH_TIMEOUT)

            try:
                data += socketSubset[j].recv(lens[j])
            except Exception as e:
                print(f"J: {j}; Socket: {socketSubset[j]}")

            if time.time() - start_time > RECV_TOTAL_TIMEOUT:
                break
        
        time.sleep(0.01)
        print(data)
        # if data != datas[j]:

        #     sys.stderr.write(f"Error: Data received is not the same as sent! \n")
        #     sys.exit(1)

# for i in range(numConnections):
#     socketList[i].close()

print("Success!")

