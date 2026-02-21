import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# Use explicitly fast models for reasoning
def get_llm():
    # Will fail securely if GROQ_API_KEY is not in environment
    return ChatGroq(temperature=0, model_name="llama-3.3-70b-versatile")

def invoke_agent(system_prompt: str, user_prompt: str, pydantic_schema=None):
    """Generic wrapper for invoking the LLM with structured output."""
    llm = get_llm()
    
    if pydantic_schema:
        parser = PydanticOutputParser(pydantic_object=pydantic_schema)
        # Combine instructions with format instructions
        format_instructions = parser.get_format_instructions()
        sys_msg = f"{system_prompt}\n\nMUST adhere exactly to this JSON schema:\n{format_instructions}"
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", sys_msg),
            ("user", "{input}")
        ])
        
        chain = prompt | llm | parser
        return chain.invoke({"input": user_prompt})
        
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])
        chain = prompt | llm
        return chain.invoke({"input": user_prompt})
