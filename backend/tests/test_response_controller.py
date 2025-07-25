from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_responses_endpoint_success():
    response = client.post(
        "/responses/",
        json={"question": "What was the top-selling product in October 2024?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "sql_query" in data
    assert "result" in data
    assert data["error"] is None or isinstance(data["error"], str)


def test_responses_endpoint_invalid_query():
    response = client.post("/responses/", json={"question": "DROP TABLE df;"})
    data = response.json()
    assert data["error"] is not None
    assert data["result"] is None or data["result"] == []


def test_save_and_list_responses():
    from app.services.response_service import ResponseService

    service = ResponseService()
    # Guardar una respuesta
    question = "Test question?"
    sql_query = "SELECT 1;"
    result = [{"value": 1}]
    status = "success"
    error_message = None
    service.save_response(question, sql_query, result, status, error_message)
    # Listar respuestas y verificar que la guardada está presente
    responses = service.list_responses()
    assert any(
        r["question"] == question and r["sql_query"] == sql_query for r in responses
    )
    service.close()
