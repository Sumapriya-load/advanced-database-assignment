from flask import Flask, render_template, request, redirect, url_for, flash
from database import Pet, Kind, db, initialize
from peewee import DoesNotExist

app = Flask(__name__)
app.secret_key = 'supersecret'

# Initialize Database if it doesn't exist.
db.connect()
if not db.table_exists('pet'):
    initialize()
db.close()

@app.before_request
def before_request():
    db.connect()

@app.after_request
def after_request(response):
    db.close()
    return response

@app.route('/')
def index():
    pets = Pet.select()
    return render_template("index.html", pets=pets)

@app.route('/pet/<int:pet_id>')
def view_pet(pet_id):
    try:
        pet = Pet.get_by_id(pet_id)
        return render_template("view.html", pet=pet)
    except DoesNotExist:
        flash("Pet not found.")
        return redirect(url_for('index'))

@app.route('/create', methods=['GET', 'POST'])
def create_pet():
    if request.method == "POST":
        name = request.form.get('name')
        age = request.form.get('age')
        owner = request.form.get('owner')
        kind_id = request.form.get('kind')
        try:
            kind = Kind.get(Kind.id == kind_id)
            Pet.create(name=name, age=int(age), owner=owner, kind=kind)
            flash("Pet created successfully.")
            return redirect(url_for('index'))
        except DoesNotExist:
            flash("Kind not found.")
            return redirect(url_for('create_pet'))
    kinds = Kind.select()
    return render_template("create.html", kinds=kinds)

@app.route('/update/<int:pet_id>', methods=['GET', 'POST'])
def update_pet(pet_id):
    try:
        pet = Pet.get_by_id(pet_id)
    except DoesNotExist:
        flash("Pet not found.")
        return redirect(url_for('index'))
    if request.method == "POST":
        pet.name = request.form.get('name')
        pet.age = int(request.form.get('age'))
        pet.owner = request.form.get('owner')
        kind_id = request.form.get('kind')
        try:
            pet.kind = Kind.get(Kind.id == kind_id)
            pet.save()
            flash("Pet updated successfully.")
            return redirect(url_for('index'))
        except DoesNotExist:
            flash("Kind not found.")
            return redirect(url_for('update_pet', pet_id=pet_id))
    kinds = Kind.select()
    return render_template("update.html", pet=pet, kinds=kinds)

@app.route('/delete/<int:pet_id>', methods=['GET'])
def delete_pet(pet_id):
    try:
        pet = Pet.get_by_id(pet_id)
        pet.delete_instance()
        flash("Pet deleted successfully.")
    except DoesNotExist:
        flash("Pet not found.")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
