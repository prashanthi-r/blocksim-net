# BlockSim-Net

### Prashanthi Ramachandran, Nandini Agrawal, Alptekin Küpçü and Osman Biçer

#### Abstract

Since its proposal by Eyal and Sirer (CACM '13), selfish mining attacks on proof-of-work blockchains have been studied extensively. The main body of this research aims at both studying the extent of its impact and defending against it. Yet, before any practical defense is deployed in a real world blockchain system, it needs to be tested for security and dependability. However, real blockchain systems are too complex to conduct any test on or benchmark the developed protocols. Instead, some simulation environments have been proposed recently, such as BlockSim (Maher et al., SIGMETRICS Perform. Eval. Rev. '19), which is a modular and easy-to-use blockchain simulator. However, BlockSim's structure is insufficient to capture the essence of a real blockchain network, as the simulation of an entire network happens over a single CPU. Such a lack of decentralization can cause network issues such as propagation delays being simulated in an unrealistic manner. In this work, we propose BlockSim-Net, a modular, efficient, high performance, distributed, network-based blockchain simulator that is parallelized to better reflect reality in a blockchain simulation environment.

Paper can be found here: https://arxiv.org/abs/2011.03241
