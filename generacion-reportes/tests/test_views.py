import pytest
from unittest.mock import patch
from flask import url_for


def test_ping(client_generacion_reportes):
    response = client_generacion_reportes.get('/generacion-reportes/ping')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'healthy'}


# def test_generate_report_success(client_generacion_reportes):
#     client_id = 'client123'

#     # Mock de los datos de incidentes
#     incident_data = [
#         {'status': 'OPEN'},
#         {'status': 'CLOSED'},
#         {'status': 'OPEN'},
#     ]

#     # Mock de los datos del cliente
#     client_data = {'id': client_id, 'name': 'Test Client'}

#     # Mock de la respuesta del servicio IA
#     ia_data = {'analysis': 'Análisis de ejemplo'}

#     with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
#         # Configurar side_effect para requests.get
#         mock_get.side_effect = [
#             # Primera llamada a requests.get (incidentes)
#             create_mock_response(200, incident_data),
#             # Segunda llamada a requests.get (cliente)
#             create_mock_response(200, client_data)
#         ]

#         # Configurar mock para requests.post (servicio IA)
#         mock_post.return_value = create_mock_response(200, ia_data)

#         response = client_generacion_reportes.get(f'/reports/{client_id}')
#         assert response.status_code == 200
#         data = response.get_json()

#         assert data['client'] == client_data
#         assert data['incidents'] == incident_data
#         assert data['stats']['total_incidents'] == 3
#         assert data['stats']['total_open_incidents'] == 2
#         assert data['stats']['total_closed_incidents'] == 1
#         assert 'average_resolution_time' in data['stats']
#         assert data['ia_response'] == ia_data

# def test_generate_report_incident_service_failure(client_generacion_reportes):
#     client_id = 'client123'

#     with patch('requests.get') as mock_get:
#         # Simular fallo en el servicio de incidentes
#         mock_get.return_value = create_mock_response(500, {'error': 'Internal Server Error'})

#         response = client_generacion_reportes.get(f'/reports/{client_id}')
#         assert response.status_code == 500
#         assert response.get_json() == {'error': 'Internal Server Error'}

# def test_generate_report_client_service_failure(client_generacion_reportes):
#     client_id = 'client123'

#     incident_data = [{'status': 'OPEN'}]

#     with patch('requests.get') as mock_get:
#         # Primera llamada (incidentes) exitosa
#         mock_get.side_effect = [
#             create_mock_response(200, incident_data),
#             # Segunda llamada (cliente) falla
#             create_mock_response(404, {'error': 'Client not found'})
#         ]

#         response = client_generacion_reportes.get(f'/reports/{client_id}')
#         assert response.status_code == 404
#         assert response.get_json() == {'error': 'Client not found'}

# def test_generate_report_ia_service_failure(client_generacion_reportes):
#     client_id = 'client123'

#     incident_data = [{'status': 'OPEN'}]
#     client_data = {'id': client_id, 'name': 'Test Client'}

#     with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
#         # Mock de requests.get para incidentes y cliente
#         mock_get.side_effect = [
#             create_mock_response(200, incident_data),
#             create_mock_response(200, client_data)
#         ]

#         # Mock de requests.post para el servicio IA fallido
#         mock_post.return_value = create_mock_response(500, {'error': 'IA Service Error'})

#         response = client_generacion_reportes.get(f'/reports/{client_id}')
#         assert response.status_code == 500
#         assert response.get_json() == {'error': 'IA Service Error'}

# # Función auxiliar para crear una respuesta mock
# def create_mock_response(status_code, json_data):
#     mock_resp = pytest.Mock()
#     mock_resp.status_code = status_code
#     mock_resp.json.return_value = json_data
#     return mock_resp
