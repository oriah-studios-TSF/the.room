from flask import Flask, render_template
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os

load_dotenv()

# Initialize the app
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the models
# Movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    uploaded_by = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return '<Movie %r>' % self.title

# Define the routes
# Home
@app.route('/')
def index():
    return render_template('index.html')




# Run the app
if __name__ == '__main__':
    app.run(debug=True)