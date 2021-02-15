# ## Step 2 - Climate App

# Now that you have completed your initial analysis, design a Flask API based on the queries that you have just developed.

# * Use Flask to create your routes.

# ### Routes

# * `/`

#   * Home page.

#   * List all routes that are available.

# * `/api/v1.0/precipitation`

#   * Convert the query results to a dictionary using `date` as the key and `prcp` as the value.

#   * Return the JSON representation of your dictionary.

# * `/api/v1.0/stations`

#   * Return a JSON list of stations from the dataset.

# * `/api/v1.0/tobs`
#   * Query the dates and temperature observations of the most active station for the last year of data.

#   * Return a JSON list of temperature observations (TOBS) for the previous year.

# * `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

# ## Hints

# * You will need to join the station and measurement tables for some of the queries.

# * Use Flask `jsonify` to convert your API data into a valid JSON response object.

# Import Flask
from flask import Flask, jsonify

# Dependencies and Setup
import numpy as np
import datetime as dt
import pandas as pd

# Python SQL Toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)

# Reflect Existing Database Into a New Model
Base = automap_base()
# Reflect the Tables
Base.prepare(engine, reflect=True)

# Save References to Each Table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create Session (Link) From Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary using `date` as the key and `prcp` as the value."""
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # # Starting from the most recent data point in the database. 
    
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago).\
    order_by(Measurement.date).all()
    
    precipitation_data_dict= dict(precipitation_data)

    return jsonify(precipitation_data_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""

    print("Received station api request.")

    #query stations list
    stations_data = session.query(Station).all()

    #create a list of dictionaries
    stations_list = []
    for station in stations_data:
        station_dict = {}
        station_dict["id"] = station.id
        station_dict["station"] = station.station
        station_dict["name"] = station.name
        station_dict["latitude"] = station.latitude
        station_dict["longitude"] = station.longitude
        station_dict["elevation"] = station.elevation
        stations_list.append(station_dict)

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""

    print("Received tobs api request.")

    #We find temperature data for the last year.  First we find the last date in the database
    final_date_query = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).all()
    max_date_string = final_date_query[0][0]
    max_date = dt.datetime.strptime(max_date_string, "%Y-%m-%d")

    #set beginning of search query
    begin_date = max_date - dt.timedelta(366)

    #get temperature measurements for last year
    results = session.query(Measurement).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= begin_date).all()

    #create list of dictionaries (one for each observation)
    tobs_list = []
    for result in results:
        tobs_dict = {}
        tobs_dict["date"] = result.date
        tobs_dict["station"] = result.station
        tobs_dict["tobs"] = result.tobs
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

@app.route("/api/v1.0/start")
def startDate(start):
    
    print("Server received request for 'start' page...")
    query = session.query(Measurement.tobs).filter(Measurement.date >= start).all()
    df = pd.DataFrame(query)
    tmin = df.min()
    tavg = df.mean()
    tmax = df.max()
    data = [tmin, tavg, tmax]
    data = list(np.ravel(data))
    return jsonify(data)

@app.route("/api/v1.0/start/end")
def startAndEndDate(start, end):
    print("Server received request for 'start/end' page...")
    query = session.query(Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    df = pd.DataFrame(query) 
    tmin = df.min()
    tavg = df.mean()
    tmax = df.max()
    data = [tmin, tavg, tmax]
    data = list(np.ravel(data))
    return jsonify(data)

@app.route("/")
def welcome():
    return """<html>
        <h1>Welcome to the Hawaii Climate Analysis API!<br/></h1>
        <h4>Available Routes:<br/></h4>
        <ul>
        <li><a href = "/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
        <li><a href = "/api/v1.0/stations">/api/v1.0/stations</a></li>
        <li><a href = "/api/v1.0/tobs">/api/v1.0/tobs</a></li>
        <li><a href = "/api/v1.0/start">/api/v1.0/start</a></li>
        <li><a href = "/api/v1.0/start/end">/api/v1.0/start/end</a></li>
        </ul>
        </html>"""

if __name__ == "__main__":
    app.run(debug=True)
