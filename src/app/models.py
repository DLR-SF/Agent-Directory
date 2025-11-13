from app import db


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(150))
    category = db.Column(db.String(50))
    link = db.Column(db.String(200))
    image = db.Column(db.String(200))

    def __repr__(self):
        return '<Application {}>'.format(self.name)
