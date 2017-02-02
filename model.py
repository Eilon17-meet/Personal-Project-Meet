from sqlalchemy import Column,Integer,String, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, func
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from datetime import datetime

Base = declarative_base()
#secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

# class Inventory(Base):
#     __tablename__ = 'inventory'
#     id = Column(Integer, primary_key=True)
#     product_id = Column(Integer, ForeignKey('product.id'))
#     quantity = Column(Integer)
#     last_filled = Column(DateTime, default=func.now())
#     product = relationship("Product", back_populates="inventory")


class User(Base):
	__tablename__ = 'user'
	id=Column(Integer, primary_key=True)
	name=Column(String)
	location=Column(String)
	email = Column(String(255), unique=True)
	phone_number=Column(String)
	password_hash = Column(String(255))
	songs=relationship("Song", back_populates="user")
	
	#instruments=relationship("Instrument", back_populates="user")
	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

class Song(Base):
	__tablename__ = 'song'
	id=Column(Integer, primary_key=True)
	name=Column(String)
	
	user_id = Column(Integer, ForeignKey('user.id'))
	user=relationship("User", back_populates="songs")

'''
class Instrument(Base):
	__tablename__ = 'instrument'
	id=Column(Integer, primary_key=True)
	name=Column(String)
	#time_played=Column(Integer)
	#type_of_time_played=Column(String)
	user_id = Column(Integer, ForeignKey('user.id'))
	user=relationship("User", back_populates="instrument")
'''



engine = create_engine('sqlite:///database.db')


Base.metadata.create_all(engine)
