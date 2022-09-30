#this class holds the information needed for each edge
class Edge:
    
    def __init__(self, from_node, to_node, from_time, to_time, trainNo):
        self.from_node = from_node
        self.to_node = to_node
        self.from_time=from_time
        self.to_time=to_time
        self.trainNo=trainNo