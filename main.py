from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

    def to_dic(self):
        cafe_dic = {
            "id": self.id,
            "name": self.name,
            "map_url": self.map_url,
            "img_url": self.img_url,
            "location": self.location,
            "seats": self.seats,
            "has_toilet": self.has_toilet,
            "has_wifi": self.has_wifi,
            "has_sockets": self.has_sockets,
            "can_take_calls": self.can_take_calls,
            "coffee_price": self.coffee_price,
        }
        return cafe_dic


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def finding_random_cafe():
    cafe = db.session.query(Cafe).all()
    random_cafe = random.choice(cafe)
    cafe_dic = {
        "cafe": {
            "id": random_cafe.id,
            "name": random_cafe.name,
            "map_url": random_cafe.map_url,
            "img_url": random_cafe.img_url,
            "location": random_cafe.location,
            "seats": random_cafe.seats,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "has_sockets": random_cafe.has_sockets,
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price
        }
    }
    return jsonify(cafe_dic)


@app.get("/all")
def all():
    all_cafes = Cafe.query.all()
    all_cafe_dic = {"cafe": []}
    for i in all_cafes:
        cafe_dic = {
            "id": i.id,
            "name": i.name,
            "map_url": i.map_url,
            "img_url": i.img_url,
            "location": i.location,
            "seats": i.seats,
            "has_toilet": i.has_toilet,
            "has_wifi": i.has_wifi,
            "has_sockets": i.has_sockets,
            "can_take_calls": i.can_take_calls,
            "coffee_price": i.coffee_price,
        }
        all_cafe_dic["cafe"].append(cafe_dic)
    return jsonify(all_cafe_dic)


@app.route("/search")
def search():
    getting_value = request.args.get("loc")
    searched_cafe = Cafe.query.filter_by(location=getting_value).all()
    if searched_cafe:
        cafe_dic = [{"cafe": Cafe.to_dic(i)} for i in searched_cafe]
    else:
        cafe_dic = {"error": {
            "Not Found": "Sorry we don't have a cafe at that location"
        }}
    return jsonify(cafe_dic)


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PUT", "GET"])
def updating_price(cafe_id):
    update_cafe = Cafe.query.get(cafe_id)
    if update_cafe:
        update_price = request.args.get("new_price")
        update_cafe.coffee_price = update_price
        db.session.commit()
        return jsonify({"success": "Successfully updated the price."})
    else:
        return jsonify({"error": {"Not found": "Sorry a cafe with that id wasn't found in the database."}}), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE", "GET"])
def delete(cafe_id):
    admin_api_key = "TopSecretAPIKey"
    user_api_key = request.args.get("api_key")
    delete_cafe = Cafe.query.get(cafe_id)
    if delete_cafe:
        if user_api_key == admin_api_key:
            db.session.delete(delete_cafe)
            db.session.commit()
            return jsonify({"success": "Successfully deleted the cafe."})
        else:
            return jsonify({"error": "Sorry, that's not allowed. Make sure you have the correct api-key"})
    else:
        return jsonify({"error": {"Not found": "Sorry a cafe with that id was not found in the database"}})


if __name__ == '__main__':
    app.run(debug=True)
