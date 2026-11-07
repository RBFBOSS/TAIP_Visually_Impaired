from types import SimpleNamespace

import ai.groq_client as groq_client
from ai.groq_client import GeneratedFlashcard, GeneratedStudyMaterial


def test_groq_client_requests_strict_json_and_parses_study_material(monkeypatch):
    expected = GeneratedStudyMaterial(
        summary="A short summary.",
        flashcards=[
            GeneratedFlashcard(
                question="What is the topic?",
                answer="Basic mathematics.",
                sourcePage=2,
            )
        ],
    )
    captured = {}

    def fake_groq(api_key):
        captured["api_key"] = api_key

        def create(**kwargs):
            captured["request"] = kwargs
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content=expected.model_dump_json())
                    )
                ]
            )

        return SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        )

    monkeypatch.setenv("GROQ_KEY", "test-key")
    monkeypatch.setattr(groq_client, "Groq", fake_groq)

    result = groq_client.generate_study_material("--- Page 2 ---\nLesson text")

    assert result == expected
    assert captured["api_key"] == "test-key"
    request = captured["request"]
    assert request["model"] == "openai/gpt-oss-120b"
    assert request["reasoning_effort"] == "low"
    assert request["max_completion_tokens"] == 2000
    assert request["messages"][1]["content"] == "--- Page 2 ---\nLesson text"
    response_format = request["response_format"]
    assert response_format["type"] == "json_schema"
    assert response_format["json_schema"]["strict"] is True
    schema = response_format["json_schema"]["schema"]
    assert schema["additionalProperties"] is False
    assert schema["$defs"]["GeneratedFlashcard"]["additionalProperties"] is False
