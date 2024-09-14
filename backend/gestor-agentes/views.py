# resources.py
from flask import request
from flask_restful import Resource
from models import db, Agent, UserRole
from schemas import AgentSchema
from sqlalchemy.exc import IntegrityError


agent_schema = AgentSchema()
agents_schema = AgentSchema(many=True)


class AgentRegistration(Resource):
    def post(self):
        data = request.get_json()
        try:
            name = data['name']
            email = data['email']
            password = data['password']
            role = data['role']
            identification = data['identification']
            phone = data['phone']
            address = data['address']
            city = data['city']
            state = data['state']
            zip_code = data['zip_code']
            country = data['country']
        except KeyError as e:
            return {"msg": f"Missing required field: {str(e)}"}, 400

        if Agent.query.filter_by(email=email).first():
            return {"msg": "Email already exists"}, 400

        if Agent.query.filter_by(identification=identification).first():
            return {"msg": "Identification already exists"}, 400

        try:
            role_enum = UserRole(role.lower())
        except ValueError:
            return {"msg": "Invalid role specified"}, 400

        agent = Agent(
            name=name,
            email=email,
            role=role_enum,
            identification=identification,
            phone=phone,
            address=address,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country
        )
        agent.set_password(password)

        db.session.add(agent)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"msg": "Error registering agent"}, 500

        return agent_schema.dump(agent), 201


class AgentLogin(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {"msg": "Email and password are required"}, 400

        agent = Agent.query.filter_by(email=email).first()

        if not agent or not agent.check_password(password):
            return {"msg": "Bad username or password"}, 401

        return agent_schema.dump(agent), 200


class AgentDetail(Resource):
    def get(self, agent_id):
        agent = Agent.query.get(agent_id)
        if not agent:
            return {"msg": "Agent not found"}, 404
        return agent_schema.dump(agent), 200


class Ping(Resource):
    def get(self):
        return {"status": "alive"}, 200