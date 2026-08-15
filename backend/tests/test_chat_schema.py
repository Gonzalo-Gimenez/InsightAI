import pytest

from app.schemas.chat import ChatRequest, ChatResponse


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