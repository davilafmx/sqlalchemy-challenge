from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"Enter start_date and end_date in 'YYYY-MM-DD' format for the range"
    )

@app.route("/api/v1.0/precipitation")
def precipitation(session):
    #session = Session(engine)
    year_before = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_before).all()
    precipitation = {date: prcp for date, prcp in results}
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    active_stations = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all() 
    #active_stations = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).all()   
    stations = [station for station, count in active_stations]
    #stations.sort()
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    session = Session(engine)
    temperature_last_date = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    results_2 = session.query(measurement.date, measurement.tobs).filter(measurement.date >= temperature_last_date).all()
    temp_monthly = {date: tobs for date, tobs in results_2}
    return jsonify(temp_monthly)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start=None, end=None):
    session = Session(engine)
    if not end:
        results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).all()
        temp_data = list(np.ravel(results))
        return jsonify(temp_data)

    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    temp_data = list(np.ravel(results))
    return jsonify(temp_data)


if __name__ == '__main__':
    app.run(debug=True)