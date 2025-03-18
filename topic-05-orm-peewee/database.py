import os
from peewee import *

# Create the Peewee database instance.
db = SqliteDatabase('pets.db')

class BaseModel(Model):
    class Meta:
        database = db

class Kind(BaseModel):
    name = CharField(unique=True)
    food = CharField(null=True)
    sound = CharField(null=True)

class Pet(BaseModel):
    name = CharField()
    kind = ForeignKeyField(Kind, backref='pets', on_delete='CASCADE')
    age = IntegerField()
    owner = CharField()

def initialize():
    # For demonstration, remove the existing database for a fresh start.
    if os.path.exists('pets.db'):
        os.remove('pets.db')
    db.connect()
    db.create_tables([Kind, Pet])
    # Insert sample data for Kind.
    dog = Kind.create(name="dog", food="dogfood", sound="bark")
    cat = Kind.create(name="cat", food="catfood", sound="meow")
    # Insert sample data for Pet.
    Pet.create(name="dorothy", kind=dog, age=9, owner="greg")
    Pet.create(name="suzy", kind=dog, age=8, owner="greg")
    Pet.create(name="casey", kind=cat, age=9, owner="greg")
    Pet.create(name="heidi", kind=cat, age=15, owner="david")
    db.close()

if __name__ == "__main__":
    initialize()
    print("Database initialized with sample data.")
