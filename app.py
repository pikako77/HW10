import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

### Constant
DAYS_PER_YR = 365    # Number of days in one year

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

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
#     # Create our session (link) from Python to the DB
    session = Session(engine)

    # """Convert the query results to a Dictionary using date as the key and prcp as the value.<br/>"""
    # """Return the JSON representation of your dictionary. """

    results = session.query(measurement.date, measurement.prcp ).all()

    session.close()

    data_dict = []

    for data in results:
         d = {'date': data.date , 'precipitation':data.prcp}
         data_dict.append(d)

    return jsonify(data_dict) 

@app.route("/api/v1.0/stations")
def stations():
#     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of stations from the dataset.

    results = session.query(station.station).all()

    session.close()

    all_names = list(np.ravel(results))

    return jsonify(all_names) 

@app.route("/api/v1.0/tobs")
def tobs():
#     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of stations from the dataset.
    tmp = session.query(measurement.date).order_by(measurement.date.desc()).first()
    last_date = str(tmp)[2:12]

    # get year,month and day of the last data
    yr_last,mo_last,day_last = last_date.split("-")

    # Get the date one year before the last data date
    last_date = dt.datetime(int(yr_last), int(mo_last), int(day_last))
    one_yr_b4_last_date = dt.datetime.date(last_date) - dt.timedelta(days= DAYS_PER_YR)

    results = session.query(measurement.date, measurement.tobs).\
    filter(measurement.date >= one_yr_b4_last_date).\
    order_by(measurement.date).all()

    session.close()
    data_dict = []

    for data in results:
        d = {'date': data.date , 
            'tobs':data.tobs}
        data_dict.append(d)
    
    return jsonify(data_dict) 

#@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_analysis(start_date,end_date):
    session = Session(engine)

    # if end_date==None:
    #    tmp = session.query(measurement.date).order_by(measurement.date.desc()).first()
    #    end_date = str((tmp)[2:12])

    # get date in datetime format
    # yr_last,mo_last,day_last = start_date.split("-")
    # start_date_dt = dt.datetime(int(yr_last), int(mo_last), int(day_last))

    # yr_last,mo_last,day_last = end_date[0].split("-")
    # end_date_dt = dt.datetime(int(yr_last), int(mo_last), int(day_last))

    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close()
    data_dict = []

    data_dict = {'temp_min': results[0][0] , 
             'temp_max': results[0][2] , 
             'temp_average': results[0][1] }
    

    return jsonify(data_dict)

@app.route("/api/v1.0/<start_date>")
def temp_analysis2(start_date):
    session = Session(engine)

    tmp = session.query(measurement.date).order_by(measurement.date.desc()).first()
    end_date = str(tmp)[2:12]

    # get year,month and day of the last data
    yr_last,mo_last,day_last = end_date.split("-")

    # Get the date one year before the last data date
    end_date = dt.datetime(int(yr_last), int(mo_last), int(day_last))


    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    session.close()
    data_dict = []

    data_dict = {'temp_min': results[0][0] , 
             'temp_max': results[0][2] , 
             'temp_average': results[0][1] }
    

    return jsonify(data_dict)

if __name__ == '__main__':
    app.run(debug=True, port=5000)