from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SECRET_KEY = "TopSecretAPIKey"
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    all_cafe_list = []
    for cafe in all_cafes:
        cafe_obj = {
            "id": cafe.id,
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "seats": cafe.seats,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "has_sockets": cafe.has_sockets,
            "can_take_calls": cafe.can_take_calls,
            "coffee_price": cafe.coffee_price
        }
        all_cafe_list.append(cafe_obj)
    return jsonify(cafes=all_cafe_list)


@app.route("/search")
def get_search():
    found_search = []
    # ?loc=Peckham passing parameter. loc means location.
    searched_location = request.args.get("loc").lower()
    all_cafes = db.session.query(Cafe).all()
    for cafe in all_cafes:
        if cafe.location.lower() == searched_location:
            cafe_obj = {
                "id": cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "location": cafe.location,
                "seats": cafe.seats,
                "has_toilet": cafe.has_toilet,
                "has_wifi": cafe.has_wifi,
                "has_sockets": cafe.has_sockets,
                "can_take_calls": cafe.can_take_calls,
                "coffee_price": cafe.coffee_price
            }
            found_search.append(cafe_obj)
    if len(found_search):
        return jsonify(cafes=found_search)
    else:
        return jsonify(error="Nothing_found")


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route('/update-price/<int:cafe_id>', methods=["PATCH"])
def update_cafe(cafe_id):
    all_cafes = db.session.query(Cafe).all()
    for cafe in all_cafes:
        if cafe_id == cafe.id:
            selected_cafe = Cafe.query.get(cafe_id)
            selected_cafe.coffee_price = request.form.get("new_price")
            db.session.commit()
            return jsonify(response={"success": "Successfully updated the new price."})
        else:
            return jsonify(response={"error": "No cafe id exists on given id"})


# HTTP DELETE - Delete Record
# http://127.0.0.1:5000/report-closed/21?apikey=TopSecretAPIKey
@app.route('/report-closed/<int:cafe_id>', methods=["DELETE"])
def delete_cafe(cafe_id):
    apikey = request.args.get("apikey")
    if SECRET_KEY == apikey:
        selected_cafe = Cafe.query.get(cafe_id)
        if selected_cafe:
            db.session.delete(selected_cafe)
            db.session.commit()
            return jsonify(response={"delete": "Recorde deleted"})
        else:
            return jsonify(response={"no_record": "Recorde not found"})
    else:
        return jsonify(response={"apikey_error": "API key is wrong!"})


if __name__ == '__main__':
    app.run(debug=True)
