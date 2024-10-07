import requests
from flask import current_app
from flask_restful import Resource
from auth import client_required
from config import Config


class GetReportFromClient(Resource):
    @client_required
    def post(self, current_client, client_id):
        try:
            report_response = requests.get(
                f"{Config.GENERACION_REPORTES_BASE_URL}/reports/{client_id}",
                timeout=5,
            )
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error communicating with Reports Service: {e}")
            return {"msg": "Error communicating with Reports Service"}, 503

        if report_response.status_code != 200:
            return report_response.json(), report_response.status_code

        return report_response.json(), 200