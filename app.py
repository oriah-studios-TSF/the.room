# Flask utilities used for creating the application, rendering pages, serving
# uploaded files, reading form data, and redirecting users after an action.
from flask import Flask, render_template, send_from_directory, request, url_for, redirect, flash, session
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
import uuid

# Only files with these extensions are accepted during uploads. Sets make the
# extension check quick and prevent unsupported files from being saved.
ALLOWED_MOVIE_EXTENSIONS = {'mp4', 'webm', 'mkv', 'mov'}
ALLOWED_THUMBNAIL_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}

# Load values such as SECRET_KEY and SQLALCHEMY_DATABASE_URI from .env.
load_dotenv()

# Create the Flask application instance.
app = Flask(__name__)

# Configure security and database settings. These values should normally be
# kept in environment variables rather than written directly in this file.
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Store movies and thumbnails in separate folders inside the application.
app.config["MOVIE_UPLOAD_FOLDER"] = os.path.join(app.root_path, "media", "movies")
app.config["THUMBNAIL_UPLOAD_FOLDER"] = os.path.join(app.root_path, "media", "thumbnails")

# Connect SQLAlchemy to this Flask application.
db = SQLAlchemy(app)

# Enable database schema migrations through Flask-Migrate.
migrate = Migrate(app, db)

# Enable real-time communication for chat and movie playback controls.
socketio = SocketIO(app)

# Enable login functionality.
login_manager = LoginManager(app)

login_manager.login_view = "access"

# User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Database model representing an uploaded movie.
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    uploaded_by = db.Column(db.String(100), nullable=False)
    trailer = db.Column(db.String(100), nullable=True)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return '<Movie %r>' % self.title

class Suggestions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    suggestion = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self):
        return '<Suggestion %r>' % self.suggestion

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    passcode_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.name

class Message()

# Return True when a filename has an allowed extension.
def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Access page
@app.route('/access', methods=['POST', 'GET'])
def access():
    if request.method == 'POST':
        name = request.form['name']
        passcode = request.form['passcode']
        user = User.query.filter_by(name=name).first()

        if user and check_password_hash(user.passcode_hash, passcode):
            login_user(user)
            flash('Access granted', 'success')
            return redirect(url_for('index'))
    
        flash('Invalid name or passcode', 'error')
        return redirect(url_for('access'))
        
    return render_template('access.html')

# Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('Succeccfully logged out', 'success')
    return redirect(url_for('access'))

# Home page: retrieve movies newest first and pass them to the template.
@app.route('/')
@login_required
def index():
    movies = Movie.query.order_by(Movie.uploaded_at.desc()).all()
    return render_template('index.html', movies=movies)

@app.route('/media/thumbnails/<filename>')
def thumbnail_file(filename):
    return send_from_directory(app.config['THUMBNAIL_UPLOAD_FOLDER'], filename)

@app.route('/media/movies/<filename>')
def movie_file(filename):
    return send_from_directory(app.config['MOVIE_UPLOAD_FOLDER'], filename)


# Upload page and upload processing.
@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        # Read the submitted form fields and uploaded files.
        title = request.form['title']
        description = request.form['description']
        duration = request.form['duration']
        movie_file = request.files['movie_file']
        trailer = request.form['trailer']
        thumbnail = request.files['thumbnail']

        # A thumbnail is required for every movie.
        if not thumbnail or thumbnail.filename == '':
            flash('No thumbnail file selected', 'error')
            return redirect(url_for('upload'))

        if not allowed_file(thumbnail.filename, ALLOWED_THUMBNAIL_EXTENSIONS):
            flash('Invalid thumbnail file type', 'error')
            return redirect(url_for('upload'))

        # Generate a unique name so files with identical original names do not
        # overwrite one another. secure_filename removes unsafe characters.
        thumbnail_extension = os.path.splitext(secure_filename(thumbnail.filename))[1]
        thumbnail_filename = f'{uuid.uuid4().hex}{thumbnail_extension}'
        thumbnail.save(os.path.join(app.config['THUMBNAIL_UPLOAD_FOLDER'], thumbnail_filename))

        # The movie file is optional, but if supplied it must use an accepted
        # video extension before it is saved.
        if movie_file and movie_file.filename:
            if not allowed_file(movie_file.filename, ALLOWED_MOVIE_EXTENSIONS):
                flash('Invalid movie file type', 'error')
                return redirect(url_for('upload'))
            
            movie_extension = os.path.splitext(secure_filename(movie_file.filename))[1]
            movie_filename = f'{uuid.uuid4().hex}{movie_extension}'
            movie_file.save(os.path.join(app.config['MOVIE_UPLOAD_FOLDER'], movie_filename))

        # Create a database record pointing to the generated upload names.
        movie = Movie(
            title=title,
            thumbnail=thumbnail_filename,
            description=description,
            duration=duration,
            trailer=trailer if trailer else '',
            filename=movie_filename if movie_file and movie_file.filename else '',
            uploaded_by="Oriah"
        )

        db.session.add(movie)
        db.session.commit()

        flash('Movie uploaded successfully', 'success')
        return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/watch/<int:movie_id>')
@login_required
def watch_movie(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    return render_template('watch.html', movie=movie)

@app.route('/remove/<int:movie_id>')
@login_required
def remove_from_watchlist(movie_id):
    movie = Movie.query.get_or_404(movie_id)

    # Delete files associated with the movie as well.
    if movie.filename:
        os.remove(os.path.join(app.config['MOVIE_UPLOAD_FOLDER'], movie.filename))
    if movie.thumbnail:
        os.remove(os.path.join(app.config['THUMBNAIL_UPLOAD_FOLDER'], movie.thumbnail))

    db.session.delete(movie)
    db.session.commit()

    flash('Movie removed from watchlist', 'success')
    return redirect(url_for('index'))

@app.route('/suggestion', methods=['POST', 'GET'])
@login_required
def suggestion():
    suggestions = Suggestions.query.order_by(Suggestions.uploaded_at.desc()).all()

    if request.method == 'POST':

        suggestion = request.form['suggestion']

        new_suggestion = Suggestions(suggestion=suggestion)

        db.session.add(new_suggestion)
        db.session.commit()

        flash('Suggestion submitted successfully', 'success')
        return redirect(url_for('suggestion'))
    return render_template('suggestions.html', suggestions=suggestions)

@socketio.on('send_message')
def handle_message(data):
    socketio.emit('receive_message', data)


@socketio.on('movie_play')
def handle_movie_play(data):
    socketio.emit('movie_play', data, include_self=False)


@socketio.on('movie_pause')
def handle_movie_pause(data):
    socketio.emit('movie_pause', data, include_self=False)

@socketio.on('movie_seek')
def handle_movie_seek(data):
    socketio.emit('movie_seek', data, include_self=False)

# ###
# @socketio.on('voice_call')
# def handle_voice_call():
#     socketio.emit('voice_call', include_self=False)
#
# @socketio.on('voice_offer')
# def handle_voice_offer(data):
#     socketio.emit('voice_offer', data, include_self=False)
#
# @socketio.on('voice_answer')
# def handle_voice_answer(data):
#     socketio.emit('voice_answer', data, include_self=False)
#
# @socketio.on('voice_ice_candidate')
# def handle_voice_ice_candidate(data):
#     socketio.emit('voice_ice_candidate', data, include_self=False)

# Start the development server when this file is run directly.
if __name__ == '__main__':
    socketio.run(app, debug=True)