from configparser import MAX_INTERPOLATION_DEPTH
from re import S
from tokenize import String
from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import SavedSearch, Stations , User
from . import db
import json
import csv
from timeConverter import timeToNumber, numberToTime
from graph import Graph
from routeFinder import getRouteWithArrivalTime, getRouteWithDepartureTime
from csvReader import getGraph, populateGraph, getDisabledRoutes, disableRoute, enableRoute
import folium


views = Blueprint('views', __name__)
route=[]
search=False
map=folium.Map( )
ALLOWED_EXTENSIONS = set(['csv'])

#this method recieves the search input data
#it sends the data off to get the route
#it calls the map function to get a map for the route
#it displays the output
#it also saves the search if the user is logged in
@views.route('/', methods=['GET', 'POST'])
def home():
    global route
    if request.method == 'POST':
        #get all information from search form
        departureStation = request.form.get('departureStation').upper()
        destinationStation= request.form.get('destinationStation').upper()
        searchBy=request.form["searchBy"]
        minutes = request.form.get("minutes")
        hours = request.form.get("hours")
        time=hours+":"+minutes
        day=request.form.get("day")
        #perform validation on the inputs
        if destinationStation=="" or departureStation=="":
            flash('You cannot leave any fields blank', category='error')
        elif destinationStation==departureStation:
            flash('Departure station and destination stations cannot be the same', category='error')

        elif stationExists(destinationStation)==False or stationExists(departureStation)==False:
            flash('station does not exist', category='error')
        else:
            #if inputs are valid enter here
            if current_user.is_authenticated:
                #only if user is logged in, save the search
                save_new_search(departureStation, destinationStation, searchBy, day, time,current_user.id)
            if searchBy=="depart after":
                route, time, arrivalTime = getRouteWithDepartureTime(getGraph(day), departureStation, destinationStation, timeToNumber(time))
            else:
                route, time, arrivalTime = getRouteWithArrivalTime(getGraph(day), departureStation, destinationStation, timeToNumber(time))
               
            setMap()
            stations=get_station_names()
            return render_template("home.html", user=current_user, route=route, map=map._repr_html_(), stations=stations, scroll="bottom")
    
    stations=get_station_names()
    global search
    if search==True:
        search=False
        scroll="bottom"
    else:
        scroll="top"
    return render_template("home.html", user=current_user, route=route, map=map._repr_html_(), stations=stations,scroll=scroll)


#this method saves the users search into the db
def save_new_search(departureStation, destinationStation, searchBy, day, time,id):
    new_savedSearch = SavedSearch(departureStation=departureStation, destinationStation=destinationStation, searchBy=searchBy, day=day, time=time,user_id=id)
    db.session.add(new_savedSearch)
    db.session.commit()


#this method handles the admin page.
#it recieves the uploaded csv files and sends them to the
#CSV reader to populate the graph.
#it also recieves the train number to be enabled/disabled and calls the respective methods to enable/disable them
@views.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
 if request.method == 'POST':
        if "form1" in request.form:
            file = request.files['customFile']
            if file and allowed_file(file.filename):
                try:
                    file_contents = file.stream.read().decode("utf-8")
                    day = request.form.get("day")
                    if day=="weekday":
                        path="website/static/routes_weekday.csv"
                    elif day=="saturday":
                        path="website/static/routes_saturday.csv"
                    else:
                        path="website/static/routes_sunday_holiday.csv"
                        day="sunday_holiday"
                    file1 = open(path,'wb')
                    file1.write(file_contents.encode('utf-8', 'ignore'))
                    file1.close()    
                    populateGraph(day)
                    flash('file uploaded', category='success')
                except:
                    flash('file incorrectly formatted', category='error')
            else:
                flash('incorrect file type', category='error')
        elif "form2" in request.form:
            file = request.files['stationsFile']
            try:
                if file and allowed_file(file.filename):
                    file_contents = file.stream.read().decode("utf-8")
                    path="website/static/stations.csv"
                    file1 = open(path,'wb')
                    file1.write(file_contents.encode('utf-8', 'ignore'))
                    file1.close()
                    populateStationsDb()
                    flash('file uploaded', category='success')
                else:
                    flash('incorrect file type', category='error')
            except:
                flash('file incorrectly formatted', category='error')
        else:
            if request.form["routeAvailibility"]=="Disable Route":
                disableRoute(request.form.get("routeNo"))
            else:
                enableRoute(request.form.get("routeNo"))
 users = load_all_users()
 if current_user.admin_status=="admin":
    return render_template('admin.html',user=current_user, userlist=users, disabledRoutes=getDisabledRoutes())
 else:
    flash('you do not have admin privileges', category='error')
    return render_template("home.html", user=current_user, route=route)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def populateStationsDb():
    db.session.query(Stations).delete()
    with open("website/static/stations.csv") as stations_file:
                    reader = csv.reader(stations_file)
                    for row in reader:
                        new_station = Stations(name=row[0], latitude=float(row[1]),longitude=float(row[2]))
                        db.session.add(new_station)
                        db.session.commit()

#this method gets all the users in the db
def load_all_users():
    return User.query.all()

#this method returns a list of all the station names in the db
def get_station_names():
    stationList=[]
    stations=Stations.query.all()
    for station in stations:
        stationList.append(station.name)
    return stationList

#this method sets a map showing all the stations in that route
def setMap():
    global map
    map=folium.Map( )
    minLat=140
    minLong=140
    maxLat=-100
    maxLong=-100
    stationNo=0
    for station in route:
        stationNo+=1
        stationId="1"
        for row in db.session.query(Stations).filter_by(name=station[0]):
            stationId=row.id
        current_station = Stations.query.get(stationId)
        lat=current_station.latitude
        long=current_station.longitude
        if stationNo==1:
            folium.Marker([lat,long],icon=folium.Icon(color='yellow'),).add_to(map)
        else:
            folium.Marker([lat,long]).add_to(map)
        minLat=min(lat,minLat)
        minLong=min(long,minLong)
        maxLat=max(lat,maxLat)
        maxLong=max(long,maxLong)
        if stationNo==len(route):
            for row in db.session.query(Stations).filter_by(name=station[1]):
                stationId=row.id
            current_station = Stations.query.get(stationId)
            lat=current_station.latitude
            long=current_station.longitude
            folium.Marker([lat,long], icon=folium.Icon(color='green'),).add_to(map)
        minLat=min(lat,minLat)
        minLong=min(long,minLong)
        maxLat=max(lat,maxLat)
        maxLong=max(long,maxLong)
    map.fit_bounds([[minLat, minLong], [maxLat, maxLong]]) 

#this method reurns true if the station name exists in the db
#else it returns false
def stationExists(stationName):
    for row in db.session.query(Stations).filter_by(name=stationName):
                return True
    return False
                
#when previous search is clicked,
#this method gets the data of that saved search and recomputes it
@views.route('/search-saved', methods=['POST'])
def search_saved():
    global route
    global search
    search=True
    savedSearch = json.loads(request.data)
    savedSearchId=savedSearch["savedSearchId"]
    savedSearch = SavedSearch.query.get(savedSearchId)
    departureStation= savedSearch.departureStation
    destinationStation=savedSearch.destinationStation
    searchBy=savedSearch.searchBy
    time=savedSearch.time
    day=savedSearch.day
    if searchBy=="depart after":
        route, time, arrivalTime = getRouteWithDepartureTime(getGraph(day), departureStation, destinationStation, timeToNumber(time))
    else:
        route, time, arrivalTime = getRouteWithArrivalTime(getGraph(day), departureStation, destinationStation, timeToNumber(time))
    setMap()
    return jsonify({})

#this method deletes saved searches
@views.route('/delete-savedSearch', methods=['POST'])
def delete_savedSearch():
    global route
    savedSearch = json.loads(request.data)
    savedSearchId=savedSearch["savedSearchId"]
    savedSearch = SavedSearch.query.get(savedSearchId)
    db.session.delete(savedSearch)
    db.session.commit()   
    return jsonify({})

#this method changes user type to admin user
@views.route('/make-admin', methods=['POST'])
def make_admin():
    dict = json.loads(request.data)
    userId=dict["userId"]
    user = User.query.get(userId)
    user.admin_status="admin"
    db.session.commit()   
    return jsonify({})

#this method changes user type to normal user
@views.route('/remove-admin', methods=['POST'])
def remove_admin():
    dict = json.loads(request.data)
    userId=dict["userId"]
    user = User.query.get(userId)
    user.admin_status="user"
    db.session.commit()   
    return jsonify({})

#this method deletes user accounts
@views.route('/delete-user', methods=['POST'])
def delete_user():
    dict = json.loads(request.data)
    userId=dict["userId"]
    user = User.query.get(userId)
    db.session.delete(user)
    db.session.commit()   
    return jsonify({})
