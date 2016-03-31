from sqlalchemy import Table, Column, ForeignKey, Integer, String, Date, Numeric, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import datetime
 
Base = declarative_base()

adopter_table = Table('association', Base.metadata,
    Column('adopter_id', Integer, ForeignKey('adopter.id')),
    Column('puppy_id', Integer, ForeignKey('puppy.id'))
)

class Shelter(Base):
    __tablename__ = 'shelter'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    website = Column(String)
    maximum_capacity = Column(Integer)

class Adopter(Base):
    __tablename__ = 'adopter'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    address = Column(String(250), nullable=False)
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    phone = Column(String(11), nullable=False)
    puppies = relationship("Puppy", secondary=adopter_table, back_populates='adopters')
    
class Puppy(Base):
    __tablename__ = 'puppy'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    gender = Column(String(6), nullable=False)
    dateOfBirth = Column(Date)
    picture = Column(String)
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)
    weight = Column(Integer)
    puppy_profile = relationship('Puppy_Profile', uselist=False, back_populates='puppy')
    adopters = relationship("Adopter", secondary=adopter_table, back_populates='puppies')


class Puppy_Profile(Base):
    __tablename__ = 'puppy_profile'
    profile_id = Column(Integer, primary_key=True)
    puppy_id = Column(Integer, ForeignKey('puppy.id'))
    needs = Column(String(250))
    about = Column(String(250))
    puppy = relationship('Puppy', back_populates='puppy_profile')

engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.create_all(engine)

# query for python shell
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

# Add some functionality to interact with the database a bit
def occupancy(id, name=' '):
    current_occupancy = session.query(Shelter.id, Shelter.name, func.count(Puppy.name)).join(Puppy).group_by(Shelter.name)
    for shelter in current_occupancy:
        if shelter[0] == id or shelter[1] == name:
            return shelter[2]

def max_occupancy(shelter_id, name=' '):
    max_occupancy = session.query(Shelter.maximum_capacity).filter(Shelter.id == shelter_id)
    return max_occupancy[0][0]

def shelter_name(shelter_id):
    name = session.query(Shelter.name).filter(Shelter.id == shelter_id)
    return name[0][0]

def check_availability():
    available = session.query(Shelter.name, Shelter.maximum_capacity, Shelter.id, Shelter.city)
    i = 0
    for shelter in available:
        if occupancy(shelter.id) < shelter.maximum_capacity:
            spaces = shelter.maximum_capacity - occupancy(shelter.id)
            print (shelter.name + ' in ' + shelter.city + ' currently has ' + str(spaces) + ' open spaces.')
        else:
            i = i + 1 
    if i == 0:  
        print ('No shelters are available, please open a new one.')


def add_puppy(name, gender, dob, picture, shelter_id, weight):
    current_occ  = occupancy(shelter_id)
    max_occ = max_occupancy(shelter_id)
    spaces = max_occ - current_occ
    if (current_occ + 1) < max_occ:
        puppy = Puppy(name = name, gender = gender, dateOfBirth = dob, picture = picture, shelter_id = shelter_id, weight = weight)
        session.add(puppy)
        session.commit()
        pup = session.query(Puppy).filter(Puppy.name == name)
        for puppy in pup:
            confirm_add = (puppy.name + ' is now living at ' + puppy.shelter.name)
            if spaces <= 0:
                print confirm_add
                print ('There is no more room at ' + puppy.shelter.name)
            elif spaces == 0:
                print confirm_add
                print ('There is only one more space at ' + puppy.shelter.name)
            else:
                print confirm_add
                print (puppy.shelter.name + ' can hold ' \
                    + str((spaces)) + ' more puppies.')
    else:
        print (shelter_name(shelter_id) + ' is full. Please find another shelter for poor ' + name + '.')
        check_availability()

def adopt_puppy(adopter_id, puppy_id):
    adopter = session.query(Adopter).filter(Adopter.id == adopter_id).first()
    puppy = session.query(Puppy).filter(Puppy.id == puppy_id).first()
    total_puppies = len(adopter.puppies)
    adopter.puppies.append(puppy)
    if len(adopter.puppies) == total_puppies + 1:
        shelter = puppy.shelter_id
        print occupancy(shelter)
        puppy.shelter_id = 0
        print (adopter.name + ' is now the owner of ' + adopter.puppies[total_puppies].name)
        print occupancy(shelter)

# add_puppy('George', 'Male', datetime.date(2016, 1, 3), '', 3, 15)

adopt_puppy(1, 1)

# # query for printing out names
# alphaPup = session.query(Puppy).order_by(Puppy.name).all()
# for puppy in alphaPup:
# 	print puppy.name

# sixMonth = session.query(Puppy).order_by(Puppy.dateOfBirth).all()
# for puppy in sixMonth:
# 	if puppy.dateOfBirth > datetime.date(2015, 9, 28):
# 		print puppy.name
# 		print puppy.dateOfBirth
# 		print '\n'

# weight = session.query(Puppy).order_by(Puppy.weight.desc()).all()
# for puppy in weight:
# 	print puppy.name
# 	print puppy.weight