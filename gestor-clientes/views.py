import hashlib
from flask_restful import Resource
from flask import request
from models import db, Client, Plan
from sqlalchemy.exc import IntegrityError
from schemas import ClientSchema, PlanSchema, ClientPlanSchema

client_schema = ClientSchema()
plan_schema = PlanSchema()
client_plan_schema = ClientPlanSchema()


class ClientRegistration(Resource):
    def post(self):
        data = request.get_json()
        try:
            name = data["name"]
            email = data["email"]
            password = data["password"]
            company_name = data["company_name"]

        except KeyError as e:
            return {"msg": f"Missing required field: {str(e)}"}, 400

        if Client.query.filter_by(email=email).first():
            return {"msg": "Email already exists"}, 400

        client = Client(name=name, email=email, company_name=company_name)
        client.set_password(password)

        db.session.add(client)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Error registering agent"}, 500

        return client_schema.dump(client), 201


class ClientLogin(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"msg": "Email and password are required"}, 400

        client = Client.query.filter_by(email=email).first()

        if not client or not client.check_password(password):
            return {"msg": "Bad username or password"}, 401

        return client_schema.dump(client), 200
    
class ClientDetail(Resource):
    def get(self, client_id):
        client = Client.query.get(client_id)
        if not client:
            return {"msg": "Client not found"}, 404
        return client_schema.dump(client), 200

    def put(self, client_id):
        client = Client.query.get(client_id)
        if not client:
            return {"msg": "Client not found"}, 404

        data = request.get_json()
        try:
            client.name = data["name"]
            client.email = data["email"]
            client.company_name = data["company_name"]
        except KeyError as e:
            return {"msg": f"Missing required field: {str(e)}"}, 400

        db.session.add(client)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Error updating client"}, 500

        return client_schema.dump(client), 200

    def delete(self, client_id):
        client = Client.query.get(client_id)
        if not client:
            return {"msg": "Client not found"}, 404

        db.session.delete(client)
        db.session.commit()

        return {"msg": "Client deleted"}, 200


class Plans(Resource):
    def get(self):
        plans = Plan.query.all()
        return plan_schema.dump(plans, many=True), 200

    def post(self):
        data = request.get_json()
        try:
            nombre = data["nombre"]
            descripcion = data["descripcion"]
        except KeyError as e:
            return {"msg": f"Missing required field: {str(e)}"}, 400

        plan = Plan(nombre=nombre, descripcion=descripcion)

        db.session.add(plan)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Error registering plan"}, 500

        return plan_schema.dump(plan), 201


class PlanDetail(Resource):
    def get(self, plan_id):
        plan = Plan.query.get(plan_id)
        if not plan:
            return {"msg": "Plan not found"}, 404
        return plan_schema.dump(plan), 200

    def put(self, plan_id):
        plan = Plan.query.get(plan_id)
        if not plan:
            return {"msg": "Plan not found"}, 404

        data = request.get_json()
        try:
            plan.nombre = data["nombre"]
            plan.descripcion = data["descripcion"]
        except KeyError as e:
            return {"msg": f"Missing required field: {str(e)}"}, 400

        db.session.add(plan)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Error updating plan"}, 500

        return plan_schema.dump(plan), 200

    def delete(self, plan_id):
        plan = Plan.query.get(plan_id)
        if not plan:
            return {"msg": "Plan not found"}, 404

        db.session.delete(plan)
        db.session.commit()

        return {"msg": "Plan deleted"}, 200


class ClientPlan(Resource):
    def put(self, client_id):
        client = Client.query.get(client_id)
        if not client:
            return {"msg": "Client not found"}, 404

        data = request.get_json()
        try:
            plan_id = data["plan_id"]
        except KeyError as e:
            return {"msg": f"Missing required field: {str(e)}"}, 400

        plan = Plan.query.get(plan_id)
        if not plan:
            return {"msg": "Plan not found"}, 404

        client.plan_id = plan_id
        db.session.add(client)
        db.session.commit()

        return client_schema.dump(client), 200
    
    def get(self, client_id):
        client = Client.query.get(client_id)
        if not client:
            return {"msg": "Client not found"}, 404

        plan = Plan.query.get(client.plan_id)
        if not plan:
            return {"msg": "Plan not found"}, 404

        return client_plan_schema.dump(plan), 200


class DeleteClientPlan(Resource):
    def delete(self, client_id):
        client = Client.query.get(client_id)
        if not client:
            return {"msg": "Client not found"}, 404

        client.plan_id = None
        db.session.add(client)
        db.session.commit()

        return client_schema.dump(client), 200


class SelectClientPlan(Resource):
    def post(self, client_id, plan_id):
        client = Client.query.get(client_id)
        if not client:
            return {"msg": "Client not found"}, 404

        plan = Plan.query.get(plan_id)
        if not plan:
            return {"msg": "Plan not found"}, 404

        client.plan_id = plan_id
        db.session.add(client)
        db.session.commit()

        return client_schema.dump(client), 200


class Ping(Resource):
    def get(self):
        return {"status": "healthy"}, 200
