#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Plants(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        new_plant = Plant(
            name=data['name'],
            image=data['image'],
            price=data['price'],
        )

        db.session.add(new_plant)
        db.session.commit()

        return make_response(new_plant.to_dict(), 201)


api.add_resource(Plants, '/plants')


class PlantByID(Resource):

    def record_checker(func):
        def wrapper(self, id):
            record = Plant.query.filter(Plant.id == id).first()
            if record == None:
                response_body = "<h1>404, record not found</h1>"
                response = make_response(response_body, 404)
                return response
            return func(self, record)
        return wrapper

    @record_checker
    def get(self, record):
        # plant = Plant.query.filter_by(id=id).first().to_dict()
        plant = record.to_dict()
        return make_response(jsonify(plant), 200)

    @record_checker
    def patch(self, record):
        
        try:
            request.get_json()
            [setattr(record, attr, request.json.get(attr)) for attr in request.json if hasattr(Plant, attr) and attr != "id"]
        except:
            [setattr(record, attr, request.form.get(attr)) for attr in request.form if hasattr(Plant, attr) and attr != "id"]
        
        db.session.add(record)
        db.session.commit()

        plant = record.to_dict()
        return make_response(jsonify(plant), 200)

    @record_checker
    def delete(self, record):
        db.session.delete(record)
        db.session.commit()
        response = make_response("", 204)
        return response

api.add_resource(PlantByID, '/plants/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
