from collections import defaultdict
from edge import Edge
from timeConverter import timeToNumber, numberToTime

#this class holds the data structure of all the routes
class Graph:
    def __init__(self):
        self.edges = defaultdict(list)

    #this method creates new edges and adds them to the graph
    def add_edge(self, from_node, to_node, fromTime,toTime, trainNo):
        edge=Edge(from_node, to_node, timeToNumber(fromTime),timeToNumber(toTime),trainNo)
        self.edges[from_node].append(edge)

    #this method prints out all the edges in the map    
    def displayEdgeMap(self):
        print(self.edges)