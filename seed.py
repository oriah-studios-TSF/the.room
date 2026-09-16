from app import app, db, Movie

movies = [
     Movie(
        title="Spider-Man: Into the Spider-Verse",
        thumbnail="spiderverse.jpg",
        description="Miles Morales becomes Spider-Man and discovers a world of Spider-People.",
        duration="1h 57m",
        filename="spiderverse.mp4",
        uploaded_by="Molefe"
    ),
    Movie(
        title="Interstellar",
        thumbnail="interstellar.jpg",
        description="A group of explorers travels through a wormhole in search of a new home for humanity.",
        duration="2h 49m",
        filename="interstellar.mp4",
        uploaded_by="Oriah"
    ),
    Movie(
        title="The Batman",
        thumbnail="the-batman.jpg",
        description="Batman investigates corruption and a series of murders threatening Gotham City.",
        duration="2h 32m",
        filename="the-batman.mp4",
        uploaded_by="Molefe"
    ),
    Movie(
        title="How to Train Your Dragon",
        thumbnail="how-to-train-your-dragon.jpg",
        description="A young Viking forms an unlikely friendship with a dragon.",
        duration="1h 57m",
        filename="how-to-train-your-dragon.mp4",
        uploaded_by="Oriah"
    ),
    Movie(
        title="Your Name",
        thumbnail="your-name.jpg",
        description="Two teenagers mysteriously begin experiencing each other's lives from afar.",
        duration="1h 57m",
        filename="your-name.mp4",
        uploaded_by="Molefe"
    )
]

with app.app_context():
    db.session.add_all(movies)
    db.session.commit()
    print("Movies seeded successfully!")