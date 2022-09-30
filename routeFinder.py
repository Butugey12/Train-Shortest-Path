from faulthandler import disable
from timeConverter import timeToNumber, numberToTime
from csvReader import getDisabledRoutes

#this method uses dijkstra to calculate the shortest path between 2 stations.  
#it adds additional logic to dijkstra to ensure the routes found are physically possible
#such as ensuring the train arrives before the next one can leave
def calculate(graph, origin, destination,departure_time):
    disabledRoutes=getDisabledRoutes()
    times=[]
    routeList=[]
    shortest_paths = {origin: (None, 0)}
    shortest_paths_without_trip_time = {origin: (None, 0)}
    current_station = origin
    visited_stations = list()
    latest_time = 0
    lastTrainNo=""

    while current_station != destination:

        visited_stations.append(current_station)
        available_stations = graph.edges[current_station]
        time_to_current_station = shortest_paths[current_station][1]

        for next_station in available_stations:   
            
            if int(next_station.from_time)<(time_to_current_station) or int(next_station.from_time)< departure_time or (next_station.trainNo in disabledRoutes):
                continue
            if lastTrainNo!=next_station.trainNo and (int(next_station.from_time)-time_to_current_station<3):
                continue
            trip_time = (next_station.to_time)
            
            if next_station.to_node not in shortest_paths:
                shortest_paths[next_station.to_node] = (current_station, trip_time)
                shortest_paths_without_trip_time[next_station.to_node] = (
                    current_station,
                    trip_time- time_to_current_station,
                )
            else:
                current_shortest_time = shortest_paths[next_station.to_node][1]
                if (current_shortest_time > trip_time):
                    
                    shortest_paths[next_station.to_node] = (current_station, trip_time)
                    shortest_paths_without_trip_time[next_station.to_node] = (
                        current_station,
                        trip_time- time_to_current_station,
                    )
        next_stations = dict()
        for station in shortest_paths:
            if station not in visited_stations:
                next_stations[station] = shortest_paths[station]
        if not next_stations:
            routeList=[]
            return routeList,400, 400
        current_station = min(next_stations, key=lambda k: next_stations[k][1])
        fromStation, arriveTime = shortest_paths[current_station]
        edges=graph.edges[fromStation]
        for edge in edges:
            if edge.from_node==str(fromStation) and edge.to_node==str(current_station) and edge.to_time==arriveTime and (edge.trainNo not in disabledRoutes):
                lastTrainNo=edge.trainNo
                
    while current_station:
        fromStation, arriveTime = shortest_paths[current_station]
        edges=graph.edges[fromStation]
        trainNo=""
        for edge in edges:
            if edge.from_node==str(fromStation) and edge.to_node==str(current_station) and edge.to_time==arriveTime and (edge.trainNo not in disabledRoutes):
                if trainNo==edge.trainNo:
                    trainNo=edge.trainNo
                    break
                toStationTime=edge.from_time
                times.append(int(toStationTime))
                trainNo=edge.trainNo
        if str(fromStation) != "None":
            routeList.insert(0,[fromStation,str(current_station),numberToTime(toStationTime),numberToTime(arriveTime),trainNo])
        latest_time += shortest_paths_without_trip_time[current_station][1]
        next_station = shortest_paths[current_station][0]
        current_station = next_station
    return routeList,times[len(times)-1], latest_time


#this method calls the calculate method and is used to find the best route when the departure time is specified
def getRouteWithDepartureTime(graph, origin, destination,departure_time):
    route, time, arrivalTime =  calculate(graph, origin, destination, departure_time)
    # return calculate(graph, origin, destination, departure_time)
    return getRouteWithArrivalTime(graph, origin, destination, arrivalTime+1)



#this method uses the calculate method but alters the inputs, making
#it find the best route when arrival time is specified
def getRouteWithArrivalTime(graph, origin, destination, arrival_time):
    arrival_time=arrival_time+1
    departure_time=arrival_time
    bol=True
    while bol==True:
        departure_time=departure_time-2
        route, departT,arriveT = calculate(graph, origin, destination,departure_time)
        if (departure_time<=400):
            bol=False
            return [], departT, arriveT
        if (route==[] and departure_time>400):
            bol=True
        elif(arriveT>=arrival_time ):
            bol=True
        else:
            bol=False
            return route, departT, arriveT
    return route, departT, arriveT