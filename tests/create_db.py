import datetime
from sqlalchemy import create_engine, Column, Integer, String, Date, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

class Trainer(Base):
    __tablename__ = 'Trainer'
    trainer_id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    dob = Column(Date())
    tiger_skills = Column(Float())


engine = create_engine("sqlite:///workspaces/datadock/tests/tigerking.db", echo=True)
Base.metadata.create_all(engine)

trainers = [
    Trainer(first_name='Joe', last_name='Exotic', dob=datetime.date(1963, 3, 5), tiger_skills=0.7),
    Trainer(first_name='Carole', last_name='Baskin', dob=datetime.date(1961, 6, 6), tiger_skills=0.3),
    Trainer(first_name='Bhagavan', last_name='Antle', dob=datetime.date(1960, 3, 25), tiger_skills=1.0)
]

Session = sessionmaker(bind=engine)
session = Session()

session.add_all(trainers)
session.commit()






