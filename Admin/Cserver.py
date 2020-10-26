import socket
import threading
import pickle
from InputsConfig import InputsConfig as p
from LightTransaction import Transaction as txn
from Node import Node as Node
import numpy as np
import time
from datetime import datetime
class Cserver:
    
    global IP
    IP=socket.gethostbyname(socket.gethostname())
    global PORT
    PORT=8002

    def connect():
        print("-------------------CONNECT------------------------\n\n")
        #should be able to listen to all the nodes simultaenously
        #IP ='172.31.4.248'
       	#IP=socket.gethostbyname(socket.gethostname())
        #PORT = 8002
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server_socket.bind((IP,PORT))
        server_socket.listen(p.Nn)

        print('Started listening')
        cur_id = 0
        while True:
            client_socket, addr = server_socket.accept() #client_socket refers to other VMs
            print("\nGot connection from", addr)
            data = pickle.loads(client_socket.recv(1024))
            hp = data[0]
            p.HASH_INFO.append(hp)
            server_port = data[1]
            client_socket.send(str(cur_id).encode()) # send the node its ID
            p.total_hashpower += hp
            client_socket.close()
            info_obj = {
                "id": cur_id,
                "IP": addr[0],
                "PORT": server_port
            }
            p.NODES_INFO.append(info_obj)
            if(len(p.NODES_INFO)==p.Nn):
                server_socket.close()                
                return
            else: 
                cur_id=cur_id+1

    def send_nodes_info():
        print("-----------------SEND NODES INFO--------------------------\n\n")
        if(p.Nn>1):
            for i in range(p.Nn):
                info = []
                info.append(p.total_hashpower)
                print("total_hashpower: ",p.total_hashpower)
                for j in range(p.Nn):
                    if(i!=j):
                        info.append(p.NODES_INFO[j])
                info = pickle.dumps(info)
                node_as_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                print("IP :",p.NODES_INFO[i]['IP'])
                print("Port :",p.NODES_INFO[i]['PORT'])
                # time.sleep(1)
                node_as_client.connect((p.NODES_INFO[i]['IP'],p.NODES_INFO[i]['PORT']))
                node_as_client.send(info)
                node_as_client.close()
                print('Sent NODE_INFO to ',p.NODES_INFO[i]['PORT'])
           
    def send_txnpool_gblock():
        print("-----------------------------SEND TXNS AND GENESIS BLOCK-----------------------------\n\n")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server_socket.bind((IP, PORT))
        server_socket.listen(p.Nn)

        block = Node.generate_gensis_block()
        if(p.hasTrans):
            txnpool = txn.pending_transactions # this works only for light txns
            txn_genbl = pickle.dumps([txnpool,block])
        else:
            txn_genbl = pickle.dumps(block)
        # the nodes will connect to the central server when they want to get the txn pool and genesis block
        count=0
        while True:
            if count<p.Nn:
                client_socket, addr = server_socket.accept() #client_socket refers to nodes
                print("\nGot connection from", addr)
                client_socket.send(txn_genbl)
                count+=1
                client_socket.close()
            else:
                server_socket.close()
                return

    def getChain(minerId,depth):
        longestBlockchain = ["Simulation Discarded!!!"]
        if(p.Nn>1):
            for i in range(p.Nn):
                node_as_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                node_as_client.connect((p.NODES_INFO[i]['IP'],(p.NODES_INFO[i]['PORT']-2)))
                mID = int(node_as_client.recv(1024).decode())
                if mID==minerId:
                    y = 1
                    node_as_client.send(str(y).encode())
                    # try:
                    longestBlockchain = pickle.loads(node_as_client.recv(8192))
                    print("Received longest blockchain from miner ",minerId)
                        # print(longestBlockchain)
                    # except:
                        # print("Miner "+str(minerId)+" who has the longest chain doesnt have a complete chain")

                else:
                    y = 0
                    node_as_client.send(str(y).encode())

                node_as_client.close()

        return longestBlockchain

    def getLastBlock():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server_socket.bind((IP, PORT))
        server_socket.listen(p.Nn)

        maxLength = -1 # length of the longest blockchain
        minerId = -1 # id of the miner with the longest blockchain
        count=0
        allAddr=[]
        #get last block from miners and determine the miner with the longest chain
        while True:
            if count<p.Nn:
                client_socket, addr = server_socket.accept()
                if count==0:
                    timestamp=datetime.now()     
                print("\nGot connection from", addr)
                blockRecv = pickle.loads(client_socket.recv(2048)) #miner id + last block
                print("Miner's block depth: ", blockRecv[1].depth)
                if(blockRecv[1].depth>=maxLength and blockRecv[1].timestamp<timestamp):
                    maxLength=blockRecv[1].depth
                    timestamp=blockRecv[1].timestamp
                    minerId=blockRecv[0]                           
                count+=1
                client_socket.close()
            else:
                server_socket.close()
                break

        return minerId,maxLength

    def consensus():
        print("-------------------------------CONSENSUS---------------------------\n\n")
        
        minerId,maxLength=Cserver.getLastBlock()
        print("Miner ID of the miner with the longest chain: ", minerId)
        p.longestBlockchain=Cserver.getChain(minerId,maxLength)
        

        #send chain to everyone
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        server_socket.bind((IP, PORT))
        server_socket.listen(p.Nn)

        count=0
        while True:
            if count<p.Nn-1:
                client_socket, addr = server_socket.accept() 
                print("\nGot connection from", addr)
                client_socket.send(pickle.dumps(p.longestBlockchain))
                client_socket.close()   
                count+=1
            else:
                server_socket.close()
                break



