from model import *

engine = create_engine('sqlite:///database.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()


eilon_email='eilon246810@gmail.com'
eilon_password='eilon123'
eilon_phone='0526937304'

song= Song(
	name='SONG1',
	user_id=1
	)



session.add(song)

eilon = User(
	name = 'Eilon',
	email=eilon_email,
	phone_number=eilon_phone,
	location='Tivon, Israel'
	)
eilon.hash_password(eilon_password)
session.add(eilon)
session.commit()