from InputsConfig import InputsConfig as p
from Queue import Queue
from Transaction import Transaction
from Event import Event
from Consensus import Consensus
from Scheduler import Scheduler
# from Results import Results
from Node import Node
from server import Nodethread
#from VerifTest import VerifTest
# import scipy as sp
import numpy as np
import math
import statistics
import threading
import pickle
import datetime

########################################################## Start Simulation ##############################################################
    
def main():

    Nodethread.connect()
    print('Now about to get info')
    Nodethread.recvnodesinfo()
    # one thread will start listening for blocks from other nodes

    for i in range (p.Runs):
        t1 = threading.Thread(target=Nodethread.listen)
        p.stop_receive_blocks = False
        t1.start()
        print('Started thread and now running the rest')
        
        p.startSimTime = datetime.datetime.now()
        print('Start Time: ', p.startSimTime)
        p.endSimTime = p.startSimTime+datetime.timedelta(seconds=p.simTime)
        print('End Time: ', p.endSimTime)

        Nodethread.recv_txns_genblock()
        Scheduler.initial_events() # initiate initial events to start with

        while datetime.datetime.now() <= p.endSimTime:
            # print("Inside while")
            if (not Queue.isEmpty("create")):
                # print("create block found")
                next_create_block = Queue.get_next_create_block()
                # print("Timestamp on this block: ",next_create_block.timestamp)
                if(datetime.datetime.now() >= next_create_block.timestamp):
                    if (((p.NODE).last_block().depth < next_create_block.depth) and ((p.NODE).last_block().id == next_create_block.previous)):
                        (p.NODE).blockchain.append(next_create_block)
                        threading.Thread(Nodethread.send_block(next_create_block)).start()
                        Scheduler.create_block_event()
                        # print(next_create_block)
                    else:
                        Queue.remove_block("create")

            if (not (Queue.isEmpty("receive"))):
                next_receive_block = Queue.get_next_receive_block()
                Scheduler.receive_block_event(next_receive_block)
        
        p.stop_receive_blocks = True
        print("Stopping the thread and closing the socket...")
       
        if p.fullChain==False:
            Node.buildFullChain()

        for i in range(len((p.NODE).blockchain)):
            print("Block depth: ", (p.NODE).blockchain[i].depth, end=" ")
            print("Block id: ", (p.NODE).blockchain[i].id, end=" ")
            print("Prev block id: ", (p.NODE).blockchain[i].previous, end=" ")
            print("Timestamp: ", (p.NODE).blockchain[i].timestamp, end=" ")
            print("Miner: ", (p.NODE).blockchain[i].miner)
       
        Nodethread.consensus()

        # Consensus.longest_chain() # apply the longest chain to resolve the forks
        # Results.calculate() # calculate the simulation results (e.g., block statstics and miners' rewards)

        # ########## reset all global variable before the next run #############
        # Results.reset() # reset all variables used to calculate the results
        # Node.resetState() # reset all the states (blockchains) for all nodes in the network

    # Results.print_to_excel() # print all the simulation results in an excel file



######################################################## Run Main method #####################################################################
if __name__ == '__main__':
    main()
