from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
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
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/random', methods=['GET'])
def get_random_cafe():
    if request.method == 'GET':
        all_cafes = db.session.query(Cafe).all()
        random_cafe = random.choice(all_cafes)
        return jsonify(cafe={
            'id': random_cafe.id,
            'name': random_cafe.name,
            'map_url': random_cafe.map_url,
            'img_url': random_cafe.img_url,
            'location': random_cafe.location,
            'seats': random_cafe.seats,
            'has_toilet': random_cafe.has_toilet,
            'has_wifi': random_cafe.has_wifi,
            'has_sockets': random_cafe.has_sockets,
            'can_take_calls': random_cafe.can_take_calls,
            'coffee_price': random_cafe.coffee_price,
        })

## HTTP GET - Read Record
@app.route('/all')
def all():
    cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in cafes])

@app.route('/search')
def search():
    location_param = request.args.get("loc")
    cafes = Cafe.query.filter_by(location=location_param).all()
    if len(cafes) > 0:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, w don't have a cafe at that location."})


## HTTP POST - Create Record

@app.route('/add', methods=['POST', 'GET'])
def add_new_cafe():
    new_cafe = Cafe(
    name=request.form.get('name'),
    map_url=request.form.get('map_url'),
    img_url=request.form.get('img_url'),
    location=request.form.get('img_url'),
    seats=request.form.get('seats'),
    has_toilet=bool(request.form.get('has_toilet')),
    has_wifi=bool(request.form.get('has_wifi')),
    has_sockets=bool(request.form.get('has_sockets')),
    can_take_calls=bool(request.form.get('can_take_calls')),
    coffee_price=request.form.get('coffee_price'),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record

@app.route('/update-price/<cafe_id>', methods=['PATCH', 'GET', 'POST'])
def update_price(cafe_id):
    cafe_to_update = Cafe.query.get(cafe_id)
    if cafe_to_update:
        new_price = request.args.get("new_price")
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


## HTTP DELETE - Delete Record

@app.route('/report-closed/<cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    API_KEY = "123456789"
    cafe_to_delete = Cafe.query.get(cafe_id)
    entered_api_key = request.args.get("api-key")
    if API_KEY == entered_api_key:
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe"})
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})
    else:
        return jsonify(error={"Error": "Sorry that's not allowed. Make sure you have the correct api key."})

if __name__ == '__main__':
    app.run(debug=True)
