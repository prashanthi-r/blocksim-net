import operator
# from InputsConfig import InputsConfig as p

class Queue:

    create_block_list=[]
    receive_block_list=[]

    def add_block(type,block):
        if (type=="create"):
            Queue.create_block_list += [block]
        else: 
            Queue.receive_block_list += [block]

    def remove_block(type):
        if (type=="create"):
            del Queue.create_block_list[0]
        else: 
            del Queue.receive_block_list[0]

    def get_next_create_block():
        Queue.create_block_list.sort(key=operator.attrgetter('timestamp'), reverse=False) # sort block -> earliest one first
        return Queue.create_block_list[0]

    def get_next_receive_block():
        Queue.receive_block_list.sort(key=operator.attrgetter('timestamp'), reverse=False) # sort block -> earliest one first
        return Queue.receive_block_list[0]

    def size(type):
        if(type=="create"):
            return len(Queue.create_block_list)
        else:
            return len(Queue.receive_block_list)

    def isEmpty(type):
        if (type=="create"):
            return len(Queue.create_block_list) == 0
        else: 
            return len(Queue.receive_block_list) == 0