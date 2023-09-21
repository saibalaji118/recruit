from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import MetaData, create_engine
from flask_cors import CORS
from application import app

uri = "postgresql://saibalaji:RbgceTFY04sorWYVOIDL@database-1.c6l9b0w4xvbk.ap-south-1.rds.amazonaws.com:5432/my_first_db"
app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = create_engine(uri)
meta = MetaData()
meta.reflect(bind=engine)

db = SQLAlchemy(app)


# db.create_all()

# Enable CORS so that we can make HTTP request from frontend server
CORS(app, origins='*')


# Models
class UserSession(db.Model):
    __tablename__ = 'user_session'
    email = db.Column(db.String(120), primary_key=True, nullable=False)
    username = db.Column(db.String(120), nullable=False)
    login_time = db.Column(db.TIMESTAMP)
    resume_file_link = db.Column(db.String(255))
    result_file_link = db.Column(db.String(255))


    # def __init__(self, email, username):
    #     self.email = email
    #     self.username = username