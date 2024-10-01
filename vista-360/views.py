from flask_restful import Resource
from flask import request
from models import db, UserSchema, User


class UsersView(Resource):
    def post(self):
        return {"message": "usuario creado exitosamente"}, 201

    def get(self):
        return {
            "usuarios": [
                {
                    "name": "usuario 1",
                }
            ]
        }, 200


class UserView(Resource):
    def get(self, user_id):
        return {"name": f"usuario {user_id}"}, 200


class Ping(Resource):
    def get(self):
        return {"status": "healthy"}
