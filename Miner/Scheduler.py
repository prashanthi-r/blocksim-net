
from InputsConfig import InputsConfig as p
import random
from Transaction import Transaction
from Block import Block
from Event import Event
from Queue import Queue
from Node import Node
from Consensus import Consensus as c
import socket
import pickle
import datetime

###################################### A class to schedule future events ########################################
class Scheduler:

    ##variable initialisation
    # def __init__(self):
    #     self.node = p.NODE
    # ##### Time methods #####
    # def PoW_completion_time(hashPower):
    #     return random.expovariate(hashPower * 1/p.Binterval)
    def receive_block_time():
        return random.expovariate(1/p.Bdelay)


    # ##### Start solving a fresh PoW on top of last block appended #####
    # def solve_PoW(miner):
    #     TOTAL_HASHPOWER = sum([miner.hashPower for miner in p.NODES])
    #     hashPower = miner.hashPower/TOTAL_HASHPOWER
    #     return Scheduler.PoW_completion_time(hashPower)
    ##### Schedule initial events and add them to the event list #####
    def initial_events():
        print("========INITIATE EVENT==========")
        if p.hashPower >0: # only if hashPower >0, the node will be eligiable for mining
            Scheduler.create_block_event()

    ##### Schedule a block creation event and add it to the event list #####
    def create_block_event():
        print("===========CREATE BLOCK============")
        node = p.NODE
        if p.hashPower > 0:
            currentTime = datetime.datetime.now()
            # blockTime = currentTime + Scheduler.solve_PoW(miner)
            blockTime = datetime.timedelta(seconds = c.PoW())
            blockTime = currentTime + blockTime
            # eventTime = blockTime
            # eventType = "create_block"

            # eventTime <= simstarttime+p.simTime
            if blockTime <= p.endSimTime: ##### create the event + add it to the event list #####
                # prepare attributes for the event
                minerId= p.id
                blockDepth= len(node.blockchain)
                blockId= random.randrange(100000000000)
                blockPrev= node.last_block().id
                print("BlockPrev: ", blockPrev)

                block = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],0,[]) # event content: transactions, uncles and blockSize is not set yet -> they will be set once the event is created
                # event = Event(eventType,minerId,eventTime,block) # create the event
                Queue.add_block("create",block) # add the event to the queue
                

    ### This function is run only once our block is created in run_event(), cant send event before block is created
    def receive_block_event(block):
        node = p.NODE
        blockDepth = block.depth
        blockId = block.id
        blockTrans = block.transactions
        blockPrev= block.previous
        blockSize = block.size
        blockTime = block.timestamp
        blockUncles= block.uncles
        lastBlockId = node.last_block().id
        minerId= block.miner

        #### case 1: the received block is built on top of the last block according to the recipient's blockchain ####
        if blockPrev == lastBlockId:
            block=Block(blockDepth,blockId, blockPrev,blockTime,minerId,blockTrans,blockSize,blockUncles) # construct the block
            node.blockchain.append(block) # append the block to local blockchain
            print("Appended block: ",blockId)
            if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node, block)
            Scheduler.create_block_event()

        #### case 2: the received block is  not built on top of the last block ####
        else:
            depth = blockDepth + 1
            if (depth > len(node.blockchain)):
                Node.update_local_blockchain(blockId) 
                print("Need to update local blockchain")
                Scheduler.create_block_event()
            #### 2- if depth of the received block <= depth of the last block, then reject the block (add it to unclechain) ####
            else:
              uncle = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],0,[]) # construct the uncle block
              node.unclechain.append(uncle)

        if p.hasUncles: Node.update_unclechain(node)
        if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node,block) # not sure yet.
        
        Queue.remove_block("receive")
