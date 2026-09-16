from flask import Flask, render_template, send_from_directory, request, url_for, redirect, flash
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from werkzeug.utils import secure_filename
import uuid

ALLOWED_MOVIE_EXTENSIONS = {'mp4', 'webm', 'mkv', 'mov'}
ALLOWED_THUMBNAIL_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

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

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

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

    if request.method == 'POST':
        title = request.form['title']
        desciption = request.form['description']
        duration = request.form['duration']
        movie_file = request.files['movie_file']
        thumbnail = request.files['thumbnail']

        if not thumbnail or thumbnail.filename == '':
            flash('No thumbnail file selected', 'error')
            return redirect(url_for('upload'))

        if not allowed_file(thumbnail.filename, ALLOWED_THUMBNAIL_EXTENSIONS):
            flash('Invalid thumbnail file type', 'error')
            return redirect(url_for('upload'))

        thumbnail_extension = os.path.splitext(secure_filename(thumbnail.filename))[1]
        thumbnail_filename = f'{uuid.uuid4().hex}{thumbnail_extension}'
        thumbnail.save(os.path.join(app.config['THUMBNAIL_UPLOAD_FOLDER'], thumbnail_filename))

        if movie_file and movie_file.filename:
            if not allowed_file(movie_file.filename, ALLOWED_MOVIE_EXTENSIONS):
                flash('Invalid movie file type', 'error')
                return redirect(url_for('upload'))
            
            movie_extension = os.path.splitext(secure_filename(movie_file.filename))[1]
            movie_filename = f'{uuid.uuid4().hex}{movie_extension}'
            movie_file.save(os.path.join(app.config['MOVIE_UPLOAD_FOLDER'], movie_filename))

        movie = Movie(
            title=title,
            thumbnail=thumbnail_filename,
            description=desciption,
            duration=duration,
            filename=movie_filename if movie_file and movie_file.filename else '',
            uploaded_by="Oriah"
        )

        db.session.add(movie)
        db.session.commit()

        flash('Movie uploaded successfully', 'success')
        return redirect(url_for('index'))
    return render_template('upload.html')





# Run the app
if __name__ == '__main__':
    app.run(debug=True)