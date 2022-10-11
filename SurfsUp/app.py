import numpy as np
from requests import session
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine(
    "sqlite:///C:/Users/User/Desktop/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/temp/<start><br>"
        f"/api/v1.0/temp/<start>/<end><br>"
    )

# create precipitation route of last 12 months of precipitation data


@app.route("/api/v1.0/precipitation")
def prcp():
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    Query = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= query_date).all()
    session.close()

    # convert results to a dictionary with date as key and prcp as value
    precipitation_dict = {date: prcp for date, prcp in Query}

    # return json list of dictionary
    return jsonify(precipitation_dict)

# create station route of a list of the stations in the dataset


@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.name, Station.station).all()
    # convert results to a dict
    stations_dict = dict(stations)

    # return json list of dict (I decided to do a dict instead of a list here to show both the station name and the station number)
    return jsonify(stations_dict)


# create tobs route of temp observations for most active station over last 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    tobs_station = session.query(Measurement.tobs)\
        .filter(Measurement.date >= query_date)\
        .filter(Measurement.station == "USC00519281").all()
    session.close()
   # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(tobs_station))

    # return json list of dict
    return jsonify(temps=temps)


# create start and start/end route
# min, average, and max temps for a given date range
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def start_date(start=None, end=None):

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(
        Measurement.tobs), func.max(Measurement.tobs)]
    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()

        session.close()

        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)


if __name__ == '__main__':
    app.run(debug=True)
