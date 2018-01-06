from random import *

from model import *

engine = create_engine('postgres://wnhfzdmxqiwjjh:8303f7e3899346cf3160f14b33f334a61505629ce61bdd1ae4c38250fb34771d@ec2-54-227-250-33.compute-1.amazonaws.com:5432/df1iuch3j1v8gi')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

for i in range(1, 6):
    a1 = Comment(
        text='Comment test number ' + str(i),
        customer_id=1,
        product_id=1,
        stars=randint(1, 5)
    )

    session.add(a1)

session.commit()
