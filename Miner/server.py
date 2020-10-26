import socket
import threading
import pickle
from Queue import Queue
from InputsConfig import InputsConfig as p
from Node import Node
from Scheduler import Scheduler
import datetime
from Block import Block
import time

class Nodethread:
    global myIP
    myIP=socket.gethostbyname(socket.gethostname())
    
    # connect to central server at [cs_ip,cs_port] and send my IP, port, hashpower information
    def connect():
        print("--------------CONNECT------------------\n\n")
        node_as_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("CS IP:",p.cs_ip)
        node_as_client.connect((p.cs_ip, p.cs_port))
        send_init_info = [p.hashPower, p.myPort] # populate list and send hashPower, server_port
        send_init_info = pickle.dumps(send_init_info)
        node_as_client.send(send_init_info) 
        p.id = int(node_as_client.recv(1024).decode())
        print("My ID: ", p.id)
        p.NODE = Node(p.id,p.hashPower)
        node_as_client.close() 

    # receive information about other nodes from the central server
    def recvnodesinfo():
        print("--------------RECEIVE NODES INFO------------------\n\n")
        if(p.Nn>1):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #the SO_REUSEADDR flag tells the kernel to
            server_socket.bind((myIP, p.myPort))
            server_socket.listen(1)
            print('Listening')
            while True:
                try:
                    client_socket, addr = server_socket.accept() # wait for the central server to connect
                    break
                except:
                    continue
            print('Connected')
            info = []
            info = pickle.loads(client_socket.recv(4096)) 
            p.total_hashpower = info[0]
            print("total_hashpower= ",p.total_hashpower)
            if(len(info)>1):
                p.NODES_INFO = info[1:].copy()
            client_socket.close()
            server_socket.close()
        else:
            p.total_hashpower = p.hashPower
        return 

    def recv_txns_genblock():
        print("----------------RECEIVE TXNS AND GENESIS BLOCK---------------\n\n")
        node_as_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                node_as_client.connect((p.cs_ip, p.cs_port))
                break
            except: 
                continue
        txn_genbl = pickle.loads(node_as_client.recv(2048))
        if(p.hasTrans):
            txns = txn_genbl[0]
            (p.NODE).blockchain.append(txn_genbl[1]) # add genesis block to node's blockchain
        else:
            (p.NODE).blockchain.append(txn_genbl)
        node_as_client.close()    
    

    def receive_block(client_socket,addr):
        print("-----------------RECEIVE BLOCK-------------------------\n\n")
        print('Connected: ',addr)
        block = pickle.loads(client_socket.recv(2048)) # kept it 2048 instead of 1024 as im guessing Events obj is big
        (p.NODE).network_blocks[block.id] = block
        Queue.add_block("receive",block)
        print('Block recieved from ',addr)
        print('Block id',block.id)
        print('Block miner',block.miner)
        print("Added to network_blocks")
        client_socket.close()

    # listen continuously to other nodes for new blocks
    def listen():
        #should be able to listen to all the nodes simultaenously
        print("------------------LISTEN FOR BLOCKS----------------------\n\n")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.settimeout(10)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #the SO_REUSEADDR flag tells the kernel to
        server_socket.bind((myIP, p.myPort))
        server_socket.listen(p.Nn)
        print('Started listening')
        while True:
            if p.stop_receive_blocks:
               print("Server socket closed. Returning...")
               server_socket.close() 
               return
            else:
                try:
                    client_socket, addr = server_socket.accept() #client_socket refers to other VMs
                    print("\nGot connection from", addr)
                    threading.Thread(target=Nodethread.receive_block, args=(client_socket,addr)).start()
                except:
                    continue

    # send created block to other nodes
    def send_block(block):
        print("---------------------SEND BLOCK---------------------------\n\n")
        # miner= event.node
        blockDepth = block.depth
        blockId = block.id
        blockTrans = block.transactions
        blockPrev= block.previous
        blockSize = block.size
        blockTimestamp = block.timestamp
        blockUncles= block.uncles

        block = Block(blockDepth,blockId,blockPrev,blockTimestamp,p.id,blockTrans,blockSize,blockUncles)
        (p.NODE).network_blocks[blockId] = block
        print("New block created and added to network_blocks")
        send_block = pickle.dumps(block)

        # if(blockDepth==2): # for checking a certain case 
        #     time.sleep(20)

        for i in range(p.Nn-1):
            receive_block_time = blockTimestamp +datetime.timedelta(seconds = Scheduler.receive_block_time())
            if receive_block_time <= p.endSimTime: # receive_block_time <= simstarttime+p.simTime
                node_as_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                node_as_client.connect((p.NODES_INFO[i]['IP'], p.NODES_INFO[i]['PORT']))
                node_as_client.send(send_block)
                node_as_client.close()
                print('Sent Event information to ',p.NODES_INFO[i]['PORT'])

        Queue.remove_block("create")
        return


    def sendChain():
        # print("--Send/Check for longest chain--")
        if(p.Nn>1):
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #the SO_REUSEADDR flag tells the kernel to
            server_socket.bind((myIP, (p.myPort-2)))
            server_socket.listen(1)
            client_socket, addr = server_socket.accept() # wait for the central server to connect
            client_socket.send(str(p.id).encode())
            y = int(client_socket.recv(1024).decode())
            if y==1:
                if p.fullChain:
                    client_socket.send(pickle.dumps((p.NODE).blockchain)) 
                    # print('---Sent my blockchain---')      
            else: 
                print("My blockchain is not the longest.")
            
            client_socket.close()
            server_socket.close()
        return y

    def sendLastBlock():
        # print("--Send Last Block--")
        node_as_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        node_as_client.connect((p.cs_ip, p.cs_port))

        sendBlock=[]
        sendBlock.append(p.id)
        sendBlock.append((p.NODE).last_block())
        last_block = pickle.dumps(sendBlock)
        node_as_client.send(last_block)
        node_as_client.close()
     
    def consensus():
        print("------------------CONSENSUS----------------------------------\n\n")
        Nodethread.sendLastBlock()
        y=Nodethread.sendChain()

        # print("--Print Consensus Result--")
        if y!=1:
            loopCondition=True
            print("---------------FINAL CHAIN AFTER CONSENSUS-------------")
            while loopCondition:
                try:
                    node_as_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    node_as_client.connect((p.cs_ip, p.cs_port))
                    longestBlockchain = pickle.loads(node_as_client.recv(4096))
                    for block in longestBlockchain:
                        print("Block depth ", block.depth, end=" ")
                        print("Block id: ", block.id, end=" ")
                        print("Prev block id: ", block.previous, end=" ")
                        print("Timestamp: ", block.timestamp, end=" ")
                        print("Miner: ", block.miner)
                    node_as_client.close()
                    loopCondition=False
                except:
                    continue
                    
        else:
            if p.fullChain==False:
                print('Simulation Discarded!!!')
            else:
                print('MY CHAIN IS ACCEPTED!!!')


        