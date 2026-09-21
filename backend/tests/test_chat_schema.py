import pytest

from app.schemas.chat import ChatRequest, ChatResponse, HistoryMessage, ToolResult


def test_pregunta_valida():
    request = ChatRequest(question="¿Cuál es el total de ventas?")
    assert request.question == "¿Cuál es el total de ventas?"


def test_pregunta_solo_espacios_rechazada():
    with pytest.raises(ValueError):
        ChatRequest(question="   ")


def test_pregunta_vacia_rechazada():
    with pytest.raises(ValueError):
        ChatRequest(question="")


def test_pregunta_demasiado_larga_rechazada():
    with pytest.raises(ValueError):
        ChatRequest(question="a" * 1001)


def test_question_limpia_espacios_extremos():
    request = ChatRequest(question="  ¿Total de ventas?  ")
    assert request.question == "  ¿Total de ventas?  "


def test_chat_response_model():
    response = ChatResponse(answer="respuesta")
    assert response.answer == "respuesta"


def test_chat_response_con_herramientas():
    tool = ToolResult(
        name="ventas_por_categoria",
        arguments={"categoria": "Electrónica"},
        result={"Electrónica": 1800},
    )
    response = ChatResponse(answer="respuesta", tools=[tool])
    assert response.answer == "respuesta"
    assert response.tools[0].name == "ventas_por_categoria"
    assert response.tools[0].result == {"Electrónica": 1800}


def test_historial_vacio_se_filtra():
    request = ChatRequest(
        question="Y por región?",
        history=[
            HistoryMessage(role="user", content="Cómo van las ventas?"),
            HistoryMessage(role="assistant", content="   "),
        ],
    )
    assert len(request.history) == 1
    assert request.history[0].content == "Cómo van las ventas?"