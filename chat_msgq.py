import sys 
import time
import sysv_ipc
from multiprocessing import Process, Queue



key = int(input("key :"))

try:
    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)
    
except:
    print("Message queue", key, "already exsits, terminating.")
    sys.exit(1)


my_input = 100
connect_to_neighbor = False
print("Starting time server.")

while my_input !=0:
    my_input = int(input ("0 : quit, 1 : connect with key +1 , 2 : send message, 3 : receive from neighbor msgq, 4: receive from my msgq\n"))
    
    if my_input == 1:
        try:
            mq_neighbor = sysv_ipc.MessageQueue(key+1)
            print("success ", key +1)
            connect_to_neighbor = True
            
        except :
            print("Cannot connect to message queue", key+1, ", terminating.")
            
            


    if my_input == 2:
        msg = input("message : ")
        
        mq.send(msg)
        if connect_to_neighbor == True:
            mq_neighbor.send(msg)

    if my_input == 3:
        if connect_to_neighbor == True:
            msg, _= mq_neighbor.receive()
            
            msg_decode = msg.decode()
            print("msg from ",key + 1, msg_decode)

            mq.send(msg_decode)

    if my_input == 4:
        msg, _= mq.receive()
            
        msg_decode = msg.decode()
        print("msg from ",key - 1, msg_decode)

        if connect_to_neighbor == True:
            mq_neighbor.send(msg_decode)

mq.remove()