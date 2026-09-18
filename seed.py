import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from app import app, db, User

load_dotenv()

with app.app_context():
    if not User.query.filter_by(name='Oriah').first():
        oriah = User(name='Oriah', passcode_hash=generate_password_hash(os.getenv('ORIAH_PASSCODE')))
        db.session.add(oriah)

    if not User.query.filter_by(name='Muse').first():
        muse = User(name='Muse', passcode_hash=generate_password_hash(os.getenv('MUSE_PASSCODE')))
        db.session.add(muse)

    db.session.commit()

    print('Database seeded.')




