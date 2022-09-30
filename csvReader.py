from calendar import weekday
import csv
from graph import Graph
import sys
import os.path

#there is a different graph for different days
graph_weekday = Graph()
graph_saturday = Graph()
graph_sunday_holiday = Graph()
graph_tests = Graph()


#this method reads the csv file and populates the graph
def populateGraph(day):
    path="website/static/routes_"+day+".csv"
    graph=Graph()
    with open(path) as routes_file:
                stations=[]
                trainNo=""
                reader = csv.reader(routes_file)
                for row in reader:
                    current=-1
                    if reader.line_num==1:
                        i=0
                        while (i < len(row)):
                            stations.append(row[i])
                            i=i+1
                    else:
                        i=0
                        while (i < len(row)-1):
                            if row[i+1][0]=="#":
                                current=-1
                                i=i+1
                                continue
                            if row[i][0]=="#":
                                trainNo=row[i][1:]
                                i=i+1
                                continue
                            if row[i]!="x" and row[i+1]=="x":
                                current=i
                            elif row[i]=="x" and row[i+1]!="x" and current!=-1:
                                
                                if stations[i+1][(len(stations[i+1])-2):]==" A":
                                    graph.add_edge(stations[current], stations[i+1][:(len(stations[i+1])-2)], row[current],row[i+1],trainNo)
                                else:
                                    graph.add_edge(stations[current], stations[i+1], row[current],row[i+1],trainNo)
                            elif row[i]!="x" and row[i+1]!="x":
                                if stations[i+1][(len(stations[i+1])-2):]==" A":
                                    graph.add_edge(stations[i], stations[i+1][:(len(stations[i+1])-2)], row[i],row[i+1],trainNo)
                                elif stations[i][(len(stations[i])-2):]==" D":
                                    graph.add_edge(stations[i][:(len(stations[i])-2)],stations[i+1], row[i],row[i+1],trainNo)
                                else:
                                    graph.add_edge(stations[i], stations[i+1], row[i],row[i+1],trainNo)
                            i=i+1
    if day=="weekday":
        global graph_weekday
        graph_weekday=graph

    elif day=="saturday":
        global graph_saturday
        graph_saturday=graph
    elif day=="sunday_holiday":
        global graph_sunday_holiday
        graph_sunday_holiday=graph
    else:
        global graph_tests
        graph_tests=graph


#this method returns the graph for the specific day requested through the parameters    
def getGraph(day):
    if day=="weekday":
        return graph_weekday
    elif day=="saturday":
        return graph_saturday
    elif day=="sunday_holiday":
        return graph_sunday_holiday
    else:
        return graph_tests


disabledRoutes=[]


#this method adds all the disabled trains from the csv into an array
def populateDisabledRoutes():
    global disabledRoutes
    disabledRoutes=[]

    path="website/static/disabled_routes.csv"
    with open(path) as disabledRoutes_file:
        reader = csv.reader(disabledRoutes_file)
        for row in reader:
            disabledRoutes.append(row[0])

#this disables the train by adding it to the disabled routes list
def disableRoute(routeNo):
    with open(r'website/static/disabled_routes.csv', 'a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow([routeNo])
    populateDisabledRoutes()

#this method enables trains by removing their train number from the disabled routes list
def enableRoute(routeNo):
    global disabledRoutes
    with open(r'website/static/disabled_routes.csv','w',newline='') as f:
        for route in disabledRoutes:
            if route!=routeNo:
                writer = csv.writer(f)
                writer.writerow([route])
    populateDisabledRoutes()


#this method returns a list of all the disabled trains
def getDisabledRoutes():
    populateDisabledRoutes()
    return disabledRoutes