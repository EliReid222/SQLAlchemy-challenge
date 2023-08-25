# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import pandas as pd

app = Flask(__name__)


#################################################
# Database Setup
#################################################

# Reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the tables
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
@app.route('/')
def home():
    return (
        f"Welcome to the Climate App!<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )




#################################################
# Flask Routes
#################################################

#Precipitation route
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_prior = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    one_year_prior_str = one_year_prior.strftime('%Y-%m-%d')

    # Perform a query to retrieve the precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_prior_str).all()

# Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)


# Define the Stations route
@app.route('/api/v1.0/stations')
def stations():

    # Query and retrieve the list of stations
    station_list = session.query(Station.station).all()

    # Convert the query results to a list
    stations_list = [station[0] for station in station_list]

    return jsonify(stations_list)


# Define the Temperature Observations route
@app.route('/api/v1.0/tobs')
def tobs():

    # Query and retrieve the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()[0]

    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_prior = pd.to_datetime(most_recent_date) - pd.DateOffset(years=1)
    one_year_prior_str = one_year_prior.strftime('%Y-%m-%d')

    # Perform a query to retrieve the temperature observations data
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_prior_str).\
        filter(Measurement.station == most_active_station).all()


    # Convert the query results to a list of dictionaries
    tobs_list = [{'Date': date, 'Temperature': tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

# Define the Start and End Date route
@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temperature_range(start, end=None):
    session = Session(engine)
    # Perform a query to calculate TMIN, TAVG, and TMAX for the specified date range
    if end:
        temp_data = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start, Measurement.date <= end).first()
    else:
        temp_data = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).first()

    session.close()

    tmin, tavg, tmax = results[0]
    return jsonify({
        "TMIN": tmin,
        "TAVG": tavg,
        "TMAX": tmax
    })


if __name__ == '__main__':
    app.run(debug=True)
