python3 from 
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session




#Create Path 
database_path = "sqlite:///Resources/hawaii.sqlite"
engine = create_engine(hawaii.sqlite)


#Assign Automapbase and Classes
Base = automap_base()
Base.prepare(engine, reflect=True)

Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)