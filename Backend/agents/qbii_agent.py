from Backend.agents.llm_core import invoke_agent
from Backend.models.gal_schema import (
    UserIntentRecord,
    DatasetIdentity,
    GeneratedQuestion,
)


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
        system_prompt = """You are EVA's Question Builder & Intent Inference (QBII) module.

Your job is to generate 3 to 5 SHORT, decision-focused questions for the user
so EVA can understand what they want to accomplish with this dataset.

Rules:
- Questions must be in plain language. Never ask the user to pick an algorithm,
  metric, or any technical parameter.
- Derive questions from the dataset context provided.
- Include at least one GOAL question ("What are you trying to figure out?").
- Include at least one STAKEHOLDER question ("Who will see the results?").
- Include at least one PRIORITY question ("Accuracy vs explainability?").
- Only include a TIME question if the dataset has time-series or event-log behavior.
- Each question must have a type (goal, stakeholder, priority, time) and a
  brief reason explaining why you are asking it.

Respond with a JSON object containing a single key "questions" whose value is
an array of objects with keys: question, question_type, why_asked."""

        user_prompt = f"Dataset Identity:\n{identity.model_dump_json(indent=2)}"

        # We use a lightweight inline schema here instead of the full Pydantic
        # model so the LLM output is easier to parse.
        raw = invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
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
        system_prompt = """You are EVA's Question Builder & Intent Inference (QBII) module.

You have already asked the user a set of questions. Their answers are provided below.
Your job is to infer a structured analytical intent from their responses combined with
the dataset context.

Rules:
- Determine the analysis type: prediction, explanation, segmentation, anomaly_detection, monitoring, or reporting.
- Identify stakeholder type: student, business_owner, researcher, analyst, or manager.
- Determine interpretability priority: high, moderate, or low.
- If the user's answers are vague or incomplete, infer the most likely values using
  the dataset context and record which fields were inferred (not explicitly stated).
- Conservative defaults: if unsure between explanation and prediction, choose explanation.
  If unsure about stakeholder, choose analyst. If unsure about interpretability, choose high.
- Confirm or select a target variable from the candidates if the user's goal involves prediction.

Respond with a JSON object matching the UserIntentRecord schema."""

        qa_text = "\n".join(
            f"Q: {q.question}\nA: {user_answers.get(q.question, '(no answer)')}"
            for q in questions
        )

        user_prompt = (
            f"Dataset Identity:\n{identity.model_dump_json(indent=2)}\n\n"
            f"User Q&A:\n{qa_text}"
        )

        intent = invoke_agent(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            pydantic_schema=UserIntentRecord,
        )

        # Attach the raw conversation artifacts
        intent.generated_questions = questions
        intent.user_responses = user_answers
        return intent
