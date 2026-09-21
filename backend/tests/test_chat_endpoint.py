from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@patch("app.main.ask_groq_with_tools")
@patch("app.main.ping_database")
def test_chat_endpoint_devuelve_tools(mock_ping, mock_groq):
    mock_ping.return_value = (True, 1000)
    mock_groq.return_value = (
        "Los ingresos subieron.",
        [{"name": "kpis_periodo", "arguments": {}, "result": {"kpis": {"ingresos": 1}}}],
    )

    response = client.post(
        "/api/v1/chat",
        json={"question": "¿Cómo van las ventas?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Los ingresos subieron."
    assert body["tools"][0]["name"] == "kpis_periodo"


@patch("app.main.ping_database")
def test_chat_endpoint_503_sin_db(mock_ping):
    mock_ping.return_value = (False, None)

    response = client.post(
        "/api/v1/chat",
        json={"question": "Total?"},
    )

    assert response.status_code == 503


@patch("app.main.ask_groq_with_tools")
@patch("app.main.ping_database")
def test_chat_endpoint_acepta_historial(mock_ping, mock_groq):
    mock_ping.return_value = (True, 1000)
    mock_groq.return_value = ("Ok", [])

    response = client.post(
        "/api/v1/chat",
        json={
            "question": "Y por región?",
            "history": [
                {"role": "user", "content": "Cómo van las ventas?"},
                {"role": "assistant", "content": "Los ingresos subieron."},
            ],
        },
    )

    assert response.status_code == 200
    mock_groq.assert_called_once()
    kwargs = mock_groq.call_args.kwargs
    assert kwargs["history"][0]["role"] == "user"


@patch("app.main.ask_groq_with_tools")
@patch("app.main.ping_database")
def test_chat_saludo_sin_tools_no_cambia_canvas(mock_ping, mock_groq):
    mock_ping.return_value = (True, 1000)
    mock_groq.return_value = ("Hola, ¿qué querés analizar?", [])

    response = client.post("/api/v1/chat", json={"question": "hola"})

    assert response.status_code == 200
    body = response.json()
    assert body["view"] is None
    assert body["tools"] == []
