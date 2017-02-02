from flask import *
from model import *
from flask import session as login_session

app = Flask(__name__)

engine = create_engine('sqlite:///fizzBuzz.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine, autoflush=False)
session = DBSession()

@app.route('/')
def index():
    return 'hello'














if __name__ == '__main__':
    app.run(debug=True)
