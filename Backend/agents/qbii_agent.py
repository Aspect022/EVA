from pathlib import Path
from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import (
    UserIntentRecord,
    DatasetIdentity,
    GeneratedQuestion,
)

# Path to the rules files
RULES_DIR = Path(__file__).parent.parent / "rules"

def _load_rules(filename: str) -> str:
    """Load the specified rules file for the QBII Agent."""
    path = RULES_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "(No rules file found.)"

class QBIIAgent:
    """
    Question Builder & Intent Inference Agent.

    Two-phase design matching the QBII specification:
      Phase A  – generate_questions():  Reads GAL Section 1 and produces
                 3-5 decision-focused, plain-language questions.
      Phase B  – infer_intent():        Takes user answers and infers a
                 structured UserIntentRecord for GAL Section 2.
    """

    # ------------------------------------------------------------------
    # Phase A — Generate Questions
    # ------------------------------------------------------------------
    @staticmethod
    def generate_questions(identity: DatasetIdentity) -> list[GeneratedQuestion]:
        rules = _load_rules("QuestionBuilderRules.md")
        system_prompt = f"""You are EVA's Question Builder & Intent Inference (QBII) module.

You MUST follow these Question Builder Rules:

{rules}

Respond with a JSON object containing a single key "questions" whose value is
an array of objects with keys: question, question_type, why_asked."""

        user_prompt = f"Dataset Identity (Domain: {identity.domain}):\n{identity.model_dump_json(indent=2)}"

        # We use a lightweight inline schema here instead of the full Pydantic
        # model so the LLM output is easier to parse.
        raw = invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model_type="fast_reasoning"
        )

        # Parse questions from the LLM free-text response
        import json, re

        text = raw.content if hasattr(raw, "content") else str(raw)

        # Try markdown-wrapped JSON first
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
        else:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
            else:
                raise ValueError(f"QBII failed to produce valid JSON:\n{text[:500]}")

        questions_raw = data.get("questions", [])
        return [
            GeneratedQuestion(
                question=q.get("question", ""),
                question_type=q.get("question_type", "goal"),
                why_asked=q.get("why_asked", ""),
            )
            for q in questions_raw
        ]

    # ------------------------------------------------------------------
    # Phase B — Infer Intent from User Answers
    # ------------------------------------------------------------------
    @staticmethod
    def infer_intent(
        identity: DatasetIdentity,
        questions: list[GeneratedQuestion],
        user_answers: dict[str, str],
    ) -> UserIntentRecord:
        rules = _load_rules("IntentInferenceRules.md")
        system_prompt = f"""You are EVA's Question Builder & Intent Inference (QBII) module.

You have already asked the user a set of questions. Their answers are provided below.
Your job is to infer a structured analytical intent from their responses combined with
the dataset context.

You MUST follow these Intent Inference Rules:

{rules}

Respond with a JSON object matching the UserIntentRecord schema."""

        qa_text = "\n".join(
            f"Q: {q.question}\nA: {user_answers.get(q.question, '(no answer)')}"
            for q in questions
        )

        user_prompt = (
            f"Dataset Identity (Domain: {identity.domain}):\n{identity.model_dump_json(indent=2)}\n\n"
            f"User Q&A:\n{qa_text}"
        )

        intent = invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=UserIntentRecord,
            model_type="fast_reasoning"
        )

        # Attach the raw conversation artifacts
        intent.generated_questions = questions
        intent.user_responses = user_answers
        return intent
