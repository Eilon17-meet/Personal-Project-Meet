from random import *

from model import *

engine = create_engine('sqlite:///database.db')
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
