from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re

app = Flask(__name__)

# Connect to the SQLite database and configure rows as dictionaries.
connection = sqlite3.connect("pets.db", check_same_thread=False)
connection.row_factory = sqlite3.Row

# Regular expression to allow only letters and spaces.
ALPHA_PATTERN = re.compile(r'^[A-Za-z ]+$')

def init_db():
    """Create the kind and pets tables (without the 'type' field) if they do not exist."""
    with connection:
        # Create 'kind' table first as pets references it
        connection.execute("""
            CREATE TABLE IF NOT EXISTS kind (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind_name TEXT NOT NULL
            );
        """)
        # Optionally, insert initial kinds if table is empty.
        kinds = connection.execute("SELECT COUNT(*) as count FROM kind").fetchone()
        if kinds["count"] == 0:
            connection.execute("INSERT INTO kind (kind_name) VALUES (?)", ("Dog",))
            connection.execute("INSERT INTO kind (kind_name) VALUES (?)", ("Cat",))
            connection.execute("INSERT INTO kind (kind_name) VALUES (?)", ("Bird",))
        
        # Create 'pets' table WITHOUT the 'type' column.
        connection.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                owner TEXT,
                kind_id INTEGER,
                FOREIGN KEY (kind_id) REFERENCES kind (id)
            );
        """)

# Initialize the database.
init_db()

# Home route: Redirect to the pet list.
@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("get_list"))

# Custom 404 error handler.
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route("/hello", methods=["GET"])
@app.route("/hello/<name>", methods=["GET"])
def get_hello(name="world"):
    data = [
        {"name": "bob", "age": 10},
        {"name": "suzy", "age": 8},
    ]
    return render_template("hello.html", data=data, prof={"name": name, "title": "Dr."})

@app.route("/list", methods=["GET"])
def get_list():
    cursor = connection.cursor()
    cursor.execute("""
      SELECT pets.id, pets.name, pets.age, pets.owner, kind.kind_name
      FROM pets LEFT JOIN kind ON pets.kind_id = kind.id
    """)
    rows = cursor.fetchall()
    
    pets = []
    for row in rows:
        pets.append({
            'id': row["id"],
            'name': row["name"],
            'age': row["age"],
            'owner': row["owner"],
            'kind_name': row["kind_name"]
        })
    return render_template("list.html", rows=pets)

@app.route("/create", methods=["GET"])
def get_create():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM kind")
    kinds = cursor.fetchall()
    kinds_list = [{'id': kind["id"], 'kind_name': kind["kind_name"]} for kind in kinds]
    return render_template("create.html", kinds=kinds_list)

@app.route("/create", methods=["POST"])
def post_create():
    data = dict(request.form)
    
    # Validate that age is an integer.
    age_str = data.get("age", "").strip()
    if not age_str.isdigit():
        return "Error: Age must be an integer", 400
    age = int(age_str)
    
    # Validate that name and owner contain only letters and spaces.
    name = data.get("name", "").strip()
    owner = data.get("owner", "").strip()
    if not ALPHA_PATTERN.fullmatch(name):
        return "Error: Name must only contain alphabetic characters and spaces", 400
    if not ALPHA_PATTERN.fullmatch(owner):
        return "Error: Owner must only contain alphabetic characters and spaces", 400
    
    cursor = connection.cursor()
    cursor.execute("""
       INSERT INTO pets(name, age, owner, kind_id)
       VALUES (?,?,?,?)
    """, (name, age, owner, data["kind_id"]))
    connection.commit()
    return redirect(url_for("get_list"))

@app.route("/delete/<id>", methods=["GET"])
def get_delete(id):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM pets WHERE id = ?", (id,))
    connection.commit()
    return redirect(url_for("get_list"))

@app.route("/update/<id>", methods=["GET"])
def get_update(id):
    cursor = connection.cursor()
    cursor.execute("""
       SELECT id, name, age, owner, kind_id
       FROM pets WHERE id = ?
    """, (id,))
    row = cursor.fetchone()
    if not row:
         return "Data not found."
    data = {
         "id": row["id"],
         "name": row["name"],
         "age": row["age"],
         "owner": row["owner"],
         "kind_id": row["kind_id"]
    }
    cursor.execute("SELECT * FROM kind")
    kinds = cursor.fetchall()
    kinds_list = [{'id': kind["id"], 'kind_name': kind["kind_name"]} for kind in kinds]
    return render_template("update.html", data=data, kinds=kinds_list)

@app.route("/update/<id>", methods=["POST"])
def post_update(id):
    data = dict(request.form)
    
    # Validate that age is an integer.
    age_str = data.get("age", "").strip()
    if not age_str.isdigit():
        return "Error: Age must be an integer", 400
    age = int(age_str)
    
    # Validate that name and owner contain only letters and spaces.
    name = data.get("name", "").strip()
    owner = data.get("owner", "").strip()
    if not ALPHA_PATTERN.fullmatch(name):
        return "Error: Name must only contain alphabetic characters and spaces", 400
    if not ALPHA_PATTERN.fullmatch(owner):
        return "Error: Owner must only contain alphabetic characters and spaces", 400
    
    cursor = connection.cursor()
    cursor.execute("""
       UPDATE pets SET name = ?, age = ?, owner = ?, kind_id = ? WHERE id = ?
    """, (name, age, owner, data["kind_id"], id))
    connection.commit()
    return redirect(url_for("get_list"))

if __name__ == "__main__":
    app.run(debug=True)
