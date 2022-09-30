import unittest
import csv
from csvReader import populateGraph, getGraph, enableRoute,disableRoute
from timeConverter import timeToNumber, numberToTime
from graph import Graph
from website.auth import login
from website.models import User
from routeFinder import getRouteWithDepartureTime, getRouteWithArrivalTime



class TestTrainRoute(unittest.TestCase):
    #this class initiates the graph
    def __init__(self, *args, **kwargs):
        super(TestTrainRoute, self).__init__(*args, **kwargs)
        populateGraph("tests")
        self.graph=getGraph("tests")
        

    #this method tests if the graph was populated correctly
    def test_graph_population(self):
        #normal case
        edges=self.graph.edges['A']
        self.assertEqual([edges[0].from_node, edges[0].to_node, numberToTime(edges[0].from_time),numberToTime(edges[0].to_time),edges[0].trainNo],
             ["A","B","05:10","05:13","23"])

        #skips stations
        self.assertEqual([edges[1].from_node, edges[1].to_node, numberToTime(edges[1].from_time),numberToTime(edges[1].to_time),edges[1].trainNo],
             ["A","C","06:18","06:24","30"])

        #does not start from first station
        edges=self.graph.edges['B']
        self.assertEqual([edges[3].from_node, edges[3].to_node, numberToTime(edges[3].from_time),numberToTime(edges[3].to_time),edges[3].trainNo],
             ["B","C","06:55","06:57","40"])

        #reverse routes
        edges=self.graph.edges['B']
        self.assertEqual([edges[1].from_node, edges[1].to_node, numberToTime(edges[1].from_time),numberToTime(edges[1].to_time),edges[1].trainNo],
             ["B","A","05:32","05:34","25"])

    #this method tests the time covertion from time to integer
    def test_time_to_integer(self):
        self.assertEqual(timeToNumber("00:00"), 0)
        self.assertEqual(timeToNumber("00:01"), 1)
        self.assertEqual(timeToNumber("00:12"), 12)
        self.assertEqual(timeToNumber("02:00"), 200)
        self.assertEqual(timeToNumber("14:00"), 1400)
        self.assertEqual(timeToNumber("22:23"), 2223)
    
    #this method tests the time convertion from integer to time
    def test_integer_to_time(self):
        self.assertEqual(numberToTime(0), "00:00")
        self.assertEqual(numberToTime(1), "00:01")
        self.assertEqual(numberToTime(12), "00:12")
        self.assertEqual(numberToTime(200), "02:00")
        self.assertEqual(numberToTime(1400), "14:00")
        self.assertEqual(numberToTime(2223), "22:23")
        
    #this method tests the tests the routes found is correct when departure time is specified
    def test_search_with_departure_time(self):

        #2 ajacent stations
        self.assertEqual(getRouteWithDepartureTime(self.graph, "A", "B", timeToNumber("04:00")), 
        ([['A', 'B', '05:10', '05:13', '23']], 510,513))

        #stations not adjacent
        self.assertEqual(getRouteWithDepartureTime(self.graph, "A", "E", timeToNumber("04:00")), 
           ([['A', 'B', '05:10', '05:13', '23'],
            ['B', 'C', '05:13', '05:16', '23'],
            ['C', 'D', '05:16', '05:19', '23'],
            ['D', 'E', '05:19', '05:21', '23']],
            510,521))

        #route that skips stations. and edge case as depart exactly on first train depart time
        self.assertEqual(getRouteWithDepartureTime(self.graph, "A", "E", timeToNumber("06:18")), 
           ([['A', 'C', '06:18', '06:24', '30'],
            ['C', 'E', '06:24', '06:31', '30']],
            618,631))

        #train switch needed
        self.assertEqual(getRouteWithDepartureTime(self.graph, "A", "D", timeToNumber("06:00")), 
           ([['A', 'C', '06:18', '06:24', '30'],
            ['C', 'D', '06:57', '07:00', '40']],
            618,700))

    #this method tests the tests the routes found is correct when arrival time is specified
    def test_search_with_arrival_time(self):

        #find best route with arrival time.  edge case, arrives exactly on time
        self.assertEqual(getRouteWithArrivalTime(self.graph, "A", "E", timeToNumber("10:20")), 
           ([['A', 'B', '10:00', '10:05', '50'],
            ['B', 'C', '10:05', '10:10', '50'],
            ['C', 'D', '10:10', '10:15', '50'],
            ['D', 'E', '10:15', '10:20', '50']],
            1000,1020))

        #find best route with arrival time.  train switches
        self.assertEqual(getRouteWithArrivalTime(self.graph, "A", "E", timeToNumber("13:00")), 
           ([['A', 'B', '11:00', '11:05', '60'],
            ['B', 'C', '11:05', '11:10', '60'],
            ['C', 'D', '12:10', '12:15', '70'],
            ['D', 'E', '12:15', '12:20', '70']],
            1100,1220))
    
    #this method tests the disable route functionality
    def test_disabled_route(self):
            self.assertEqual(getRouteWithDepartureTime(self.graph, "A", "E", timeToNumber("04:00")), 
           ([['A', 'B', '05:10', '05:13', '23'],
            ['B', 'C', '05:13', '05:16', '23'],
            ['C', 'D', '05:16', '05:19', '23'],
            ['D', 'E', '05:19', '05:21', '23']],
            510,521))

            disableRoute("23")

            self.assertEqual(getRouteWithDepartureTime(self.graph, "A", "E", timeToNumber("04:00")), 
           ([['A', 'C', '06:18', '06:24', '30'],
            ['C', 'E', '06:24', '06:31', '30']],
            618,631))

            enableRoute("23")





if __name__ == "__main__":
    unittest.main()
