from InputsConfig import InputsConfig as p
from Block import Block
from Transaction import Transaction
from Node import Node
from Results import Results


# class Event, which is needed to create an event as an object from this class
class Event(object):
    def __init__(self,type, node, time, block):
        self.type = type # type of event: create_block or receive_block
        self.node = node # which node
        self.time = time # the total time that will take for the event to finish executing
        self.block = block # the block associated with the event of type Block class

    def run_event (event): # run the event from the event list
        from Scheduler import Scheduler

        miner = p.NODES[event.block.miner]
        minerId = event.node
        eventTime = event.time

        blockDepth = event.block.depth
        blockId = event.block.id # block id
        blockPrev = event.block.previous # previous block id
        blockTime = event.block.timestamp
        blockTrans = event.block.transactions
        blockSize = event.block.size

        ##################################### Block Creation Event #######################################################
        if event.type == "create_block":
            if blockPrev == miner.last_block().id:
                Results.totalBlocks += 1 # count # of total blocks created!
                if p.hasTrans and p.Ttechnique == "Light": blockTrans,blockSize = LightTransaction.execute_transactions()
                elif p.hasTrans and p.Ttechnique == "Full": blockTrans,blockSize = Transaction.execute_transactions_full(miner,blockTime)
                event.block.transactions = blockTrans

                if p.hasUncles: blockUncles = Node.add_uncles(miner) # add uncles to the block
                event.block.uncles = blockUncles

                b= Block(blockDepth,blockId,blockPrev,eventTime,minerId,blockTrans,blockSize,blockUncles)
                miner.blockchain.append(b)

                if p.hasTrans and p.Ttechnique == "Light":
                    LightTransaction.create_transactions() # generate transactions

                Scheduler.receive_block_event(event) #sending our event to others since our block is now created 
                currentTime = eventTime
                Scheduler.create_block_event(miner,currentTime)

        ##################################### Block Receiving Event #######################################################
        elif event.type == "receive_block": # receive_block event

            node = p.NODE # our node
            lastBlockId= node.last_block().id # the id of last block
            blockUncles = event.block.uncles


            if (blockdepth == node.last_block().depth and node.last_block().depth==1): # the first event that is run by each miner is highly likely to be its own block which need not be 
                    if(currentTime>eventTime):
                        node.blockchain.clear()    
                        block=Block(blockDepth,blockId, blockPrev,blockTime,minerId,blockTrans,blockSize,blockUncles) # construct the block
                        node.blockchain.append(block) # append the block to local blockchain
                        if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node, event.block)
                        currentTime = eventTime # set the time when to start mining the next block
                        Scheduler.create_block_event(currentTime)

            #### case 1: the received block is built on top of the last block according to the recipient's blockchain ####
            if blockPrev == lastBlockId:
                block=Block(blockDepth,blockId, blockPrev,blockTime,minerId,blockTrans,blockSize,blockUncles) # construct the block
                node.blockchain.append(block) # append the block to local blockchain
                if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node, event.block)
                currentTime = eventTime # set the time when to start mining the next block
                Scheduler.create_block_event(currentTime)

            #### case 2: the received block is  not built on top of the last block ####
            else:
                depth = blockDepth + 1
                if (depth > len(node.blockchain)):
                    Node.update_local_blockchain(node,miner,depth)
                    currentTime = eventTime
                    Scheduler.create_block_event(currentTime)
                #### 2- if depth of the received block <= depth of the last block, then reject the block (add it to unclechain) ####
                else:
                  uncle = Block(blockDepth,blockId,blockPrev,blockTime,minerId,[],0,[]) # construct the uncle block
                  node.unclechain.append(uncle)

            if p.hasUncles: Node.update_unclechain(node)
            if p.hasTrans and p.Ttechnique == "Full": Node.update_transactionsPool(node,event.block) # not sure yet.
