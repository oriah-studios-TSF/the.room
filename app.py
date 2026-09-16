from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

load_dotenv()

# Initialize the app
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set the thumbnail upload folder
app.config["MOVIE_UPLOAD_FOLDER"] = os.path.join(app.root_path, "media", "movies")
app.config["THUMBNAIL_UPLOAD_FOLDER"] = os.path.join(app.root_path, "media", "thumbnails")

# Initialize the database
db = SQLAlchemy(app)

# Initialize the migrations
migrate = Migrate(app, db)

# Define the models
# Movie
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100), nullable=True)
    filename = db.Column(db.String(100), nullable=False)
    uploaded_by = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return '<Movie %r>' % self.title

# Define the routes
# Home
@app.route('/')
def index():
    movies = Movie.query.order_by(Movie.uploaded_at.desc()).all()
    return render_template('index.html', movies=movies)

@app.route('/media/thumbnails/<filename>')
def thumbnail_file(filename):
    return send_from_directory(app.config['THUMBNAIL_UPLOAD_FOLDER'], filename)

@app.route('/media/movies/<filename>')
def movie_file(filename):
    return send_from_directory(app.config['MOVIE_UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    return render_template('upload.html')





# Run the app
if __name__ == '__main__':
    app.run(debug=True)