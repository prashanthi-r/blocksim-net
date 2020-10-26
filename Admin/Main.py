from InputsConfig import InputsConfig as p
from Cserver import Cserver as CS
from LightTransaction import Transaction

def main(): 
	# connect to the nodes
	CS.connect()
	CS.send_nodes_info()
	
	for i in range (p.Runs):
		if p.hasTrans:
			if p.Ttechnique == "Light":
				LightTransaction.create_transactions() # generate pending transactions
			elif p.Ttechnique == "Full":
				Transaction.create_transactions_full() # generate pending transactions
		CS.send_txnpool_gblock()
		CS.consensus()

		mainBlocks = len(p.longestBlockchain)
		print("Length of blockchain: ",mainBlocks)
		num_blocks = [0]*len(p.NODES_INFO)
		for i in range(len(p.NODES_INFO)):
			for block in p.longestBlockchain[1:]:
				if(block.miner == i):
					num_blocks[i] +=1
			print("Miner ",i)
			print("Num blocks: ",num_blocks[i])			
			print("Hash Power: ",round(p.HASH_INFO[i]/p.total_hashpower*100,2))
			print("Total block percentage: ",round(num_blocks[i]/mainBlocks * 100,2))

	

######################################################## Run Main method #####################################################################
if __name__ == '__main__':
	main()
