from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, func
from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from datetime import datetime

Base = declarative_base()


# secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

# class Inventory(Base):
#     __tablename__ = 'inventory'
#     id = Column(Integer, primary_key=True)
#     product_id = Column(Integer, ForeignKey('product.id'))
#     quantity = Column(Integer)
#     last_filled = Column(DateTime, default=func.now())
#     product = relationship("Product", back_populates="inventory")


class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    address = Column(String(255))
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    when_created = Column(DateTime, default=datetime.now())
    deleted = Column(Boolean, default=False)
    when_deleted = Column(DateTime, default=None)
    comments = relationship("Comment", back_populates="customer")
    products = relationship("Product", back_populates="customer")
    favorites = relationship("Favorite", back_populates="customer")
    photo = Column(String, default='static\pic\user_pics')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Favorite(Base):
    __tablename__ = 'favorite'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship("Product", back_populates="favorite")
    customer_id = Column(Integer, ForeignKey('customer.id'))
    customer = relationship("Customer", back_populates="favorites")


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    photo = Column(String)
    price = Column(String)
    tags = Column(String)
    timestamp = Column(DateTime, default=datetime.now())
    stars = Column(Float)
    comments = relationship("Comment", back_populates="product")
    customer_id = Column(Integer, ForeignKey('customer.id'))
    customer = relationship("Customer", back_populates="products")
    favorite = relationship('Favorite', back_populates='product')


class Comment(Base):
    __tablename__ = 'comment'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now())
    text = Column(String)
    stars = Column(Integer, default=0)
    customer_id = Column(Integer, ForeignKey('customer.id'))
    customer = relationship("Customer", back_populates="comments")
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship("Product", back_populates="comments")


engine = create_engine('sqlite:///database.db')

Base.metadata.create_all(engine)
