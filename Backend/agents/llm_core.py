import os
import json
import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from Backend.config import settings

# Use explicitly fast models for reasoning
def get_llm(model_type: str = "primary"):
    """
    Returns an LLM connection based on the requested role.
    Deterministic settings for structured output.
    """
    if model_type == "reasoning":
        model_name = settings.llm.reasoning_model
    elif model_type == "fast_reasoning":
        model_name = settings.llm.fast_reasoning_model
    elif model_type == "coder":
        model_name = settings.llm.coder_model
    else:
        model_name = settings.llm.primary_model

    # Deterministic settings
    llm_params = {
        "model": model_name,
        "temperature": 0.0,
        "top_p": 1.0,
        "repeat_penalty": 1.1,  # Reasonable default
        "stream": False,
        "base_url": settings.llm.base_url,
        "timeout": settings.llm.timeout,
    }

    # Primary connection for the requested type
    requested_llm = ChatOllama(**llm_params)
    
    # Fallback to secondary model if the requested one fails
    fallback_params = llm_params.copy()
    fallback_params["model"] = settings.llm.secondary_model
    fallback_llm = ChatOllama(**fallback_params)
    
    return requested_llm.with_fallbacks([fallback_llm])


def _extract_json(text: str) -> dict:
    """
    Robustly extract JSON from LLM output.
    1. Removes markdown fences.
    2. Extracts everything between the first '{' and last '}'.
    3. Attempts to parse.
    """
    # Remove <think> blocks
    text_clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    
    # Remove markdown code fences if present
    text_clean = re.sub(r"```(?:json)?", "", text_clean)
    text_clean = re.sub(r"```", "", text_clean).strip()

    # 1. First attempt: Direct parse
    try:
        return json.loads(text_clean)
    except json.JSONDecodeError:
        pass

    # 2. Second attempt: Extract between { and }
    start_idx = text_clean.find("{")
    end_idx = text_clean.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx >= start_idx:
        json_str = text_clean[start_idx:end_idx+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Log full raw output before raising error
    print(f"\n[FATAL: JSON Extraction Failed] Raw LLM Output:\n{text}\n")
    raise ValueError(f"JSONValidationError: Managed to extract text but it was not valid JSON.")


def _coerce_to_schema(data: dict, pydantic_schema) -> dict:
    """
    Automatically coerce mismatched types so local LLM output fits the Pydantic schema.
    """
    if not pydantic_schema:
        return data
        
    schema = pydantic_schema.model_json_schema()
    properties = schema.get("properties", {})
    coerced = {}
    
    for key, value in data.items():
        if key not in properties:
            # We don't drop unexpected keys here, they'll be caught by Pydantic if extra="forbid"
            coerced[key] = value
            continue
        
        prop = properties[key]
        expected_type = prop.get("type")
        
        # Handle array fields
        if expected_type == "array":
            if isinstance(value, str):
                value = [value]
            elif value is None:
                value = []
            coerced[key] = value
        
        # Handle object/dict fields
        elif expected_type == "object":
            if isinstance(value, str):
                coerced[key] = {"summary": value}
            elif value is None:
                coerced[key] = {}
            else:
                coerced[key] = value
        
        # Handle string fields
        elif expected_type == "string":
            if value is None:
                coerced[key] = None
            elif not isinstance(value, str):
                coerced[key] = str(value)
            else:
                coerced[key] = value
        
        else:
            coerced[key] = value
    
    return coerced


def _build_example_json(pydantic_schema) -> str:
    """
    Build a concrete example JSON from a Pydantic schema.
    Clean JSON only, no placeholders like <...>.
    """
    schema = pydantic_schema.model_json_schema()
    defs = schema.get("$defs", {})
    
    def _example_from_props(properties: dict, definitions: dict) -> dict:
        example = {}
        for name, info in properties.items():
            if name in ("recorded_at", "timestamp"):  # Skip auto-generated fields
                continue
            
            ref = info.get("$ref")
            if ref:
                ref_name = ref.split("/")[-1]
                sub = definitions.get(ref_name, {})
                example[name] = _example_from_props(sub.get("properties", {}), definitions)
                continue
            
            all_of = info.get("allOf")
            if all_of:
                for item in all_of:
                    ref = item.get("$ref")
                    if ref:
                        ref_name = ref.split("/")[-1]
                        sub = definitions.get(ref_name, {})
                        example[name] = _example_from_props(sub.get("properties", {}), definitions)
                continue
            
            field_type = info.get("type", "string")
            
            if field_type == "array":
                items = info.get("items", {})
                items_ref = items.get("$ref")
                if items_ref:
                    ref_name = items_ref.split("/")[-1]
                    sub = definitions.get(ref_name, {})
                    example[name] = [_example_from_props(sub.get("properties", {}), definitions)]
                else:
                    example[name] = ["value_1"]
            elif field_type == "object":
                example[name] = {"key": "value"}
            elif field_type == "string":
                example[name] = "text_value"
            elif field_type == "integer":
                example[name] = 0
            elif field_type == "number":
                example[name] = 0.0
            elif field_type == "boolean":
                example[name] = False
            else:
                example[name] = None
        return example
    
    properties = schema.get("properties", {})
    example = _example_from_props(properties, defs)
    return json.dumps(example, indent=2)
    

def invoke_agent(system_prompt: str, user_prompt: str, pydantic_schema=None, model_type: str = "primary", rag_context: str = "", domain: str = "UNKNOWN", risk_tier: str = "UNKNOWN", debug_rag: bool = False):
    """Generic wrapper for invoking the LLM with structured output."""
    llm = get_llm(model_type)
    
    # MANDATORY JSON BLOCK - Prepend to everything
    json_guard = """
You must return ONLY valid JSON.

Rules:
- Do not include markdown.
- Do not include ```json fences.
- Do not include explanations.
- Do not include comments.
- Do not include placeholder text.
- Do not include trailing text.
- If a value is unknown, use null.
- Output must start with { and end with }.
- Output must be strictly valid JSON.

Failure to follow this format will invalidate the response.
"""
    
    system_prompt = json_guard + "\n" + system_prompt

    if rag_context:
        rag_block = (
            f"\n\n=== DOMAIN INTELLIGENCE (ADVISORY CONTEXT) ===\n"
            f"Domain: {domain}\n"
            f"Risk Tier: {risk_tier}\n\n"
            f"{rag_context}\n\n"
            f"=== GOVERNANCE RULES ARE AUTHORITATIVE ===\n"
            f"- Do NOT override risk_tier\n"
            f"- Do NOT override regulatory_mode\n"
            f"- Do NOT override interpretability_tier\n"
            f"- Do NOT invent new enum values\n"
            f"- Deterministic governance logic takes precedence\n"
        )
        system_prompt = system_prompt + rag_block

    if pydantic_schema:
        example_json = _build_example_json(pydantic_schema)
        
        json_instruction = (
            f"\n\n--- OUTPUT FORMAT ---\n"
            f"Return a single JSON object matching this structure:\n"
            f"{example_json}\n"
        )
        
        full_system = system_prompt + json_instruction
        full_system_escaped = full_system.replace("{", "{{").replace("}", "}}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", full_system_escaped),
            ("user", "{input}")
        ])
        
        chain = prompt | llm
        result = chain.invoke({"input": user_prompt})
        
        raw_text = result.content if hasattr(result, 'content') else str(result)
        
        try:
            parsed = _extract_json(raw_text)
            
            # Phase 6: Validate output before returning
            # Check for required fields
            schema_json = pydantic_schema.model_json_schema()
            required_fields = schema_json.get("required", [])
            for field in required_fields:
                if field not in parsed:
                    print(f"[Validation Error] Missing required field: {field}")
                    raise ValueError(f"JSONValidationError: Missing required field '{field}'")

            # Final cast/validation
            try:
                validated = pydantic_schema(**parsed)
                return validated
            except Exception:
                coerced = _coerce_to_schema(parsed, pydantic_schema)
                return pydantic_schema(**coerced)
                
        except Exception as e:
            raise Exception(f"{str(e)}")
        
    else:
        system_escaped = system_prompt.replace("{", "{{").replace("}", "}}")
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_escaped),
            ("user", "{input}")
        ])
        chain = prompt | llm
        return chain.invoke({"input": user_prompt})

