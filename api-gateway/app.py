from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from config import Config
from models import db
from services.incidents import *
from services.clients import *
from services.ia_service import *
from services.reports import *
from views import *


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app_context = app.app_context()
    app_context.push()

    # Initialize Extensions
    db.init_app(app)
    db.create_all()
    # migrate = Migrate(app, db)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    api = Api(app)

    # Register API resources
    api.add_resource(Login, "/agents/login", endpoint="login", methods=["POST"])
    api.add_resource(
        VerifySecurityAnswer,
        "/agents/verify-security-answer",
        endpoint="verify_security_answer",
        methods=["POST"],
    )
    api.add_resource(Ping, "/api-gateway/ping", endpoint="ping", methods=["GET"])
    api.add_resource(CreateAgent, "/agents", endpoint="create_agent", methods=["POST"])
    api.add_resource(
        DeleteAgent,
        "/agents/<string:agent_id>",
        endpoint="delete_agent",
        methods=["DELETE"],
    )
    api.add_resource(
        CreateIncident, "/incidents", endpoint="create_incident", methods=["POST"]
    )
    api.add_resource(
        DeleteIncident,
        "/incidents/<string:incident_id>",
        endpoint="delete_incident",
        methods=["DELETE"],
    )
    api.add_resource(
        UpdateIncident,
        "/incidents/<string:incident_id>",
        endpoint="update_incident",
        methods=["PUT"],
    )
    api.add_resource(
        GetIncidentsByAgent,
        "/incidents",
        endpoint="get_incidents_by_agent",
        methods=["GET"],
    )
    api.add_resource(
        GetIncidentsByUser,
        "/incidents/user/<string:user_id>",
        endpoint="get_incidents_by_user",
        methods=["GET"],
    )
    api.add_resource(
        GetIncidentsByClient,
        "/incidents/client/<string:client_id>",
        endpoint="get_incidents_by_client",
        methods=["GET"],
    )
    api.add_resource(
        GetIncidentDetail,
        "/incidents/<string:incident_id>",
        endpoint="get_incident_detail",
        methods=["GET"],
    )
    api.add_resource(Logout, "/agents/logout", endpoint="logout", methods=["POST"])
    api.add_resource(
        AdminUnlockAgent,
        "/admin/agents/<string:agent_id>/unlock",
        endpoint="admin_unlock_agent",
        methods=["POST"],
    )
    api.add_resource(
        AdminResetAgent,
        "/admin/agents/<string:agent_id>/reset",
        endpoint="admin_reset_agent",
        methods=["POST"],
    )
    api.add_resource(
        CreateClient,
        "/clients/register",
        endpoint="create_client",
        methods=["POST"],
    )
    api.add_resource(
        ClientLogin,
        "/clients/login",
        endpoint="client_login",
        methods=["POST"],
    )
    api.add_resource(
        GetClient,
        "/clients/<string:client_id>",
        endpoint="get_client",
        methods=["GET"],
    )
    api.add_resource(
        GetPlans,
        "/plans",
        endpoint="get_plans",
        methods=["GET"],
    )
    api.add_resource(
        UpdateClientPlan,
        "/clients/<string:client_id>/plan",
        endpoint="update_client_plan",
        methods=["PUT"],
    )
    api.add_resource(
        SelectClientPlan,
        "/clients/<string:client_id>/plan/<string:plan_id>",
        endpoint="select_client_plan",
        methods=["POST"],
    )
    api.add_resource(
        GetClientPlan,
        "/clients/<string:client_id>/plan",
        endpoint="get_client_plan",
        methods=["GET"],
    )
    api.add_resource(
        ChatBot,
        "/chatbot",
        endpoint="chatbot",
        methods=["POST"],
    )    
    api.add_resource(
        GetReportFromClient,
        "/reports/<string:client_id>",
        endpoint="get_report_from_client",
        methods=["POST"],
    )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
