import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app.services.groq_client import ask_groq_with_tools


def _completion(content=None, tool_calls=None):
    message = SimpleNamespace(content=content, tool_calls=tool_calls or [])
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _tool_call(name, arguments, call_id="call_1"):
    return SimpleNamespace(
        id=call_id,
        function=SimpleNamespace(name=name, arguments=json.dumps(arguments)),
    )


def test_ask_groq_invoca_herramienta_y_responde():
    execute_tool = MagicMock(return_value={"kpis": {"ingresos": 2200}})

    with patch("app.services.groq_client._client") as client:
        client.chat.completions.create.side_effect = [
            _completion(
                tool_calls=[_tool_call("kpis_periodo", {})],
            ),
            _completion(content="Los ingresos son 2200."),
        ]

        answer, tools = ask_groq_with_tools(
            "¿Cómo van las ventas?",
            [{"type": "function", "function": {"name": "kpis_periodo"}}],
            execute_tool,
        )

    assert answer == "Los ingresos son 2200."
    assert tools[0]["name"] == "kpis_periodo"
    execute_tool.assert_called_once_with("kpis_periodo", {})


def test_ask_groq_recupera_tool_call_con_nulls():
    execute_tool = MagicMock(return_value={"kpis": {"ingresos": 10}})
    failed = Exception("tool_use_failed")
    failed.body = {
        "error": {
            "code": "tool_use_failed",
            "failed_generation": json.dumps(
                {
                    "name": "kpis_periodo",
                    "arguments": {"region": None, "canal": None, "categoria": None},
                }
            ),
        }
    }

    with patch("app.services.groq_client._client") as client:
        client.chat.completions.create.side_effect = [
            failed,
            _completion(content="Ingresos 10."),
        ]
        answer, tools = ask_groq_with_tools(
            "¿Cómo van las ventas?",
            [
                {
                    "type": "function",
                    "function": {
                        "name": "kpis_periodo",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "region": {"type": "string"},
                                "canal": {"type": "string"},
                            },
                        },
                    },
                }
            ],
            execute_tool,
        )

    assert answer == "Ingresos 10."
    execute_tool.assert_called_once_with("kpis_periodo", {})
    assert tools[0]["name"] == "kpis_periodo"
