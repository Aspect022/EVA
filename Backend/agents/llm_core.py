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
    model_type can be: 'primary', 'reasoning', 'fast_reasoning', 'coder'
    """
    if model_type == "reasoning":
        model_name = settings.llm.reasoning_model
    elif model_type == "fast_reasoning":
        model_name = settings.llm.fast_reasoning_model
    elif model_type == "coder":
        model_name = settings.llm.coder_model
    else:
        model_name = settings.llm.primary_model

    # Primary connection for the requested type
    requested_llm = ChatOllama(
        model=model_name,
        temperature=settings.llm.temperature,
        base_url=settings.llm.base_url,
        timeout=settings.llm.timeout
    )
    
    # Fallback to secondary model if the requested one fails
    fallback_llm = ChatOllama(
        model=settings.llm.secondary_model,
        temperature=settings.llm.temperature,
        base_url=settings.llm.base_url,
        timeout=settings.llm.timeout
    )
    
    return requested_llm.with_fallbacks([fallback_llm])


def _extract_json(text: str) -> dict:
    """
    Robustly extract JSON from LLM output that may contain markdown wrappers,
    prose preamble, truncated output, or other non-JSON text.
    """
    # 0. Strip <think>...</think> reasoning blocks from DeepSeek/etc.
    text_clean = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    
    # 1. Try to find JSON inside markdown code blocks
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text_clean, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    
    # 2. Try to find a raw JSON object in the text (from first { to last })
    start_idx = text_clean.find("{")
    end_idx = text_clean.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = text_clean[start_idx:end_idx+1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # 3. Truncated JSON repair: LLM output was cut off, try to close braces
    if start_idx != -1:
        json_str = text_clean[start_idx:]
        # Count unclosed braces and brackets
        open_braces = json_str.count("{") - json_str.count("}")
        open_brackets = json_str.count("[") - json_str.count("]")
        # Remove trailing incomplete values (after last comma or colon)
        json_str = re.sub(r',\s*"[^"]*$', "", json_str)  # trailing key without value
        json_str = re.sub(r',\s*$', "", json_str)  # trailing comma
        json_str = re.sub(r':\s*"[^"]*$', ': ""', json_str)  # incomplete string value
        # Close remaining brackets and braces
        json_str += "]" * max(0, open_brackets) + "}" * max(0, open_braces)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Print the full payload to console for debugging
    print(f"\n[JSON Extraction Failed] Raw LLM Output:\n{text}\n")
    raise ValueError(f"No valid JSON object found in LLM output. See backend console for full response. Extract attempt was:\n{text_clean[:2000]}")


def _coerce_to_schema(data: dict, pydantic_schema) -> dict:
    """
    Automatically coerce mismatched types so local LLM output fits the Pydantic schema.
    - Strings where dicts are expected -> wrap in {"value": str}
    - Dicts where strings are expected -> json.dumps(dict)
    - Strings where lists are expected -> wrap in [str]
    """
    schema = pydantic_schema.model_json_schema()
    properties = schema.get("properties", {})
    defs = schema.get("$defs", {})
    coerced = {}
    
    for key, value in data.items():
        if key not in properties:
            coerced[key] = value
            continue
        
        prop = properties[key]
        expected_type = prop.get("type")
        
        # Handle array fields
        if expected_type == "array":
            if isinstance(value, str):
                value = [value]
            if isinstance(value, list):
                items_schema = prop.get("items", {})
                items_ref = items_schema.get("$ref")
                if items_ref:
                    # Items should be dicts matching a sub-model
                    coerced_items = []
                    for item in value:
                        if isinstance(item, str):
                            coerced_items.append({"value": item})
                        elif isinstance(item, dict):
                            coerced_items.append(item)
                        else:
                            coerced_items.append(item)
                    value = coerced_items
                elif items_schema.get("type") == "object":
                    value = [{"value": v} if isinstance(v, str) else v for v in value]
            coerced[key] = value
        
        # Handle object/dict fields
        elif expected_type == "object":
            if isinstance(value, str):
                coerced[key] = {"value": value}
            elif isinstance(value, dict):
                # Check additionalProperties to understand expected value types
                add_props = prop.get("additionalProperties", {})
                expected_val_type = add_props.get("type")
                
                if expected_val_type == "string":
                    # Values should be strings - stringify any dicts
                    coerced[key] = {k: json.dumps(v) if isinstance(v, dict) else str(v) for k, v in value.items()}
                elif expected_val_type == "object" or add_props.get("$ref"):
                    # Values should be dicts - wrap any strings
                    coerced[key] = {k: {"summary": v} if isinstance(v, str) else v for k, v in value.items()}
                else:
                    # No specific additionalProperties defined - best effort
                    # Check the actual schema hint from the field description
                    coerced_dict = {}
                    for k, v in value.items():
                        if isinstance(v, str):
                            coerced_dict[k] = {"summary": v}
                        else:
                            coerced_dict[k] = v
                    coerced[key] = coerced_dict
            else:
                coerced[key] = value
        
        # Handle string fields
        elif expected_type == "string":
            if isinstance(value, dict):
                coerced[key] = json.dumps(value)
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
    Local LLMs follow examples far more reliably than field descriptions.
    """
    schema = pydantic_schema.model_json_schema()
    defs = schema.get("$defs", {})
    
    def _example_from_props(properties: dict, required: list, definitions: dict) -> dict:
        example = {}
        for name, info in properties.items():
            if name in ("recorded_at",):  # Skip auto-generated fields
                continue
            ref = info.get("$ref")
            if ref:
                ref_name = ref.split("/")[-1]
                sub = definitions.get(ref_name, {})
                sub_props = sub.get("properties", {})
                sub_req = sub.get("required", [])
                example[name] = _example_from_props(sub_props, sub_req, definitions)
                continue
            
            all_of = info.get("allOf")
            if all_of:
                for item in all_of:
                    ref = item.get("$ref")
                    if ref:
                        ref_name = ref.split("/")[-1]
                        sub = definitions.get(ref_name, {})
                        sub_props = sub.get("properties", {})
                        sub_req = sub.get("required", [])
                        example[name] = _example_from_props(sub_props, sub_req, definitions)
                continue
            
            field_type = info.get("type", "string")
            desc = info.get("description", name)
            
            if field_type == "array":
                items = info.get("items", {})
                items_ref = items.get("$ref")
                if items_ref:
                    ref_name = items_ref.split("/")[-1]
                    sub = definitions.get(ref_name, {})
                    sub_props = sub.get("properties", {})
                    sub_req = sub.get("required", [])
                    example[name] = [_example_from_props(sub_props, sub_req, definitions)]
                else:
                    example[name] = [f"example_{name}"]
            elif field_type == "object":
                example[name] = {f"key": f"value"}
            elif field_type == "string":
                example[name] = f"<{desc}>"
            elif field_type == "integer":
                example[name] = 0
            elif field_type == "number":
                example[name] = 0.0
            elif field_type == "boolean":
                example[name] = False
            else:
                example[name] = f"<{desc}>"
        return example
    
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    example = _example_from_props(properties, required, defs)
    return json.dumps(example, indent=2)
    

def invoke_agent(system_prompt: str, user_prompt: str, pydantic_schema=None, model_type: str = "primary", rag_context: str = "", domain: str = "UNKNOWN", risk_tier: str = "UNKNOWN", debug_rag: bool = False):
    """Generic wrapper for invoking the LLM with structured output and optional RAG context."""
    llm = get_llm(model_type)
    
    # Inject RAG context into system prompt if provided
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
        
        if debug_rag:
            print("----- RAG CONTEXT LOADED -----")
            print(rag_block)
            print("--------------------------------")

    if pydantic_schema:
        # Build a concrete JSON example for the model to follow
        example_json = _build_example_json(pydantic_schema)
        
        json_instruction = (
            f"\n\n--- OUTPUT FORMAT ---\n"
            f"You MUST respond with ONLY a single valid JSON object. No markdown, no explanation, no preamble.\n"
            f"Follow this EXACT structure (use the same field names, replace placeholder values with real analysis):\n"
            f"{example_json}\n"
            f"Output raw JSON only. Do NOT change field names."
        )
        
        full_system = system_prompt + json_instruction
        
        # Escape all curly braces in the system prompt so ChatPromptTemplate
        # doesn't interpret the JSON example as template variables
        full_system_escaped = full_system.replace("{", "{{").replace("}", "}}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", full_system_escaped),
            ("user", "{input}")
        ])
        
        chain = prompt | llm
        result = chain.invoke({"input": user_prompt})
        
        # Extract JSON from the response (handles markdown wrapping, prose, etc.)
        raw_text = result.content if hasattr(result, 'content') else str(result)
        
        try:
            parsed = _extract_json(raw_text)
            # Try direct parse first
            try:
                return pydantic_schema(**parsed)
            except Exception:
                # Coerce mismatched types and retry
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

