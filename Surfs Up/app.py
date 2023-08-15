import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
from flask import Flask, jsonify
import json

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    start_date = dt.datetime(2016, 8, 23)
    end_date = dt.datetime(2017, 8, 23)

    # Query to filter by date
    filtered_entries = session.query(measurement).filter(
        (measurement.date >= start_date) & (measurement.date <= end_date)).all()

    # Extract desired key values from the filtered entries
    # desired_data = [{'date': entry.date, 'prcp': entry.prcp}
    # for entry in filtered_entries]
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= start_date).all()

    precip = {date: prcp for date, prcp in precipitation}
    session.close()
    # Convert to JSON format
    return jsonify(precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    stacion = session.query(station).all()
    data = [st.__dict__ for st in stacion]
    session.close()
    return json.dumps(data, default=str)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    start_date = dt.datetime(2016, 8, 23)
    end_date = dt.datetime(2017, 8, 23)

    most_active_station = (
        session.query(measurement.station)
        .filter(measurement.date >= start_date, measurement.date <= end_date)
        .group_by(measurement.station)
        .order_by(func.count().desc())
        .first())

    active_id = most_active_station[0]

    temp = session.query(measurement).filter(measurement.date >= start_date,
                                             measurement.date <= end_date,
                                             measurement.station == active_id).all()

    temp_list = []
    for t in temp:
        temp_dict = {"id": active_id, "date": t.date, "tobs": t.tobs}
        temp_list.append(temp_dict)

    return json.dumps(temp_list, default=str)


@app.route("/api/v1.0/<start>")
def describe(start):

    session = Session(engine)

    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    information = session.query(measurement).filter(
        measurement.date >= start_date).all()
    temp_list = []
    for info in information:
        temp_list.append(info.__dict__['tobs'])

    temp_array = np.array(temp_list)

    temp_dict = {"start-date": start, "TMIN": temp_array.min(),
                 "TAVG": temp_array.mean(),
                 "TMAX": temp_array.max()}
    return json.dumps(temp_dict, default=str)


@app.route("/api/v1.0/<start>/<end>")
def describe_2(start, end):

    session = Session(engine)
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    information = session.query(measurement).filter(
        measurement.date >= start_date, measurement.date <= end_date).all()
    temp_list = []
    for info in information:
        temp_list.append(info.__dict__['tobs'])

    temp_array = np.array(temp_list)

    temp_dict = {"start-date": start, "end-date": end, "TMIN": temp_array.min(),
                 "TAVG": temp_array.mean(),
                 "TMAX": temp_array.max()}
    return json.dumps(temp_dict, default=str)


if __name__ == '__main__':
    app.run(debug=False)
