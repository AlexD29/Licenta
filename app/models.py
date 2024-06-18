from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    url = db.Column(db.String)
    author = db.Column(db.String)
    published_date = db.Column(db.String)
    number_of_views = db.Column(db.Integer)
    image_url = db.Column(db.String)
    source = db.Column(db.Integer, db.ForeignKey('sources.id'))  # stores the source ID
    emotion = db.Column(db.Text)

    source_rel = db.relationship('Source', backref=db.backref('articles', lazy=True))

class Politician(db.Model):
    __tablename__ = 'politicians'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    city = db.Column(db.String)
    image_url = db.Column(db.String)
    date_of_birth = db.Column(db.Integer)
    position = db.Column(db.String)
    description = db.Column(db.Text)
    tags = relationship("Tag", secondary="tag_politician")

class PoliticalParty(db.Model):
    __tablename__ = 'political_parties'
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String)
    full_name = db.Column(db.String)
    description = db.Column(db.String)
    image_url = db.Column(db.String)
    tags = relationship("Tag", secondary="tag_political_party")

class City(db.Model):
    __tablename__ = 'cities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)
    image_url = db.Column(db.String)
    mayor_id = db.Column(db.String)
    population = db.Column(db.String)
    candidates_for_mayor = db.Column(db.String)
    tags = relationship("Tag", secondary="tag_city")

class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    tag_text = db.Column(db.String)
    article_id = db.Column(db.String)

class Election(db.Model):
    __tablename__ = 'elections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    date = db.Column(db.String)
    image_url = db.Column(db.String)

class Source(db.Model):
    __tablename__ = 'sources'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    image_url = db.Column(db.String)

class TagPolitician(db.Model):
    __tablename__ = 'tag_politician'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    politician_id = db.Column(db.Integer, db.ForeignKey('politicians.id'))

class TagPoliticalParty(db.Model):
    __tablename__ = 'tag_political_party'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    political_party_id = db.Column(db.Integer, db.ForeignKey('political_parties.id'))

class TagCity(db.Model):
    __tablename__ = 'tag_city'
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.id'))