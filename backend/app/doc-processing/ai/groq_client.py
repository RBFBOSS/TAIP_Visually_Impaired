import os

from groq import Groq
from pydantic import BaseModel, ConfigDict

class Citation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page_number: int
    source_excerpt: str


class GeneratedFlashcard(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)
    question: str
    answer: str
    citation: Citation


class GeneratedStudyMaterial(BaseModel):
    model_config = ConfigDict(extra="forbid")
    summary: str
    summary_citation: Citation
    flashcards: list[GeneratedFlashcard]


SYSTEM_PROMPT = (
    "You create study material for visually impaired students who listen to it "
    "with a screen reader. Use only facts from the lesson text. Write the summary "
    "in plain spoken English: short sentences, no Markdown, no tables, and no "
    "symbols that are hard to read aloud. Then write up to 10 flashcards. Each "
    "flashcard has a short question, a short answer, and the number of the page "
    "it comes from. Pages are marked like '--- Page 12 ---'."
    "For each material generated from the materials given, please generate a citation which represents the source of material generated"
    "Citation be in format of Citation schema"
)


def generate_study_material(text: str) -> GeneratedStudyMaterial:
    """Generate a summary and page-cited flashcards from selected lesson text."""
    client = Groq(api_key=os.environ.get("GROQ_KEY"))
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "study_material",
                "strict": True,
                "schema": GeneratedStudyMaterial.model_json_schema(),
            },
        },
        reasoning_effort="low",
        max_completion_tokens=2000,
    )
    return GeneratedStudyMaterial.model_validate_json(
        completion.choices[0].message.content
    )
