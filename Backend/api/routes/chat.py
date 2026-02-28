import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from Backend.config import settings
from Backend.agents.llm_core import get_llm
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    session_id: str
    messages: List[ChatMessage]

@router.get("/sessions")
def get_available_sessions():
    """
    Returns a list of all available sessions and their basic info.
    """
    sessions_dir = Path("eva_sessions")
    if not sessions_dir.exists():
        return {"sessions": []}
        
    sessions = []
    for session_path in sessions_dir.iterdir():
        if session_path.is_dir():
            session_id = session_path.name
            
            # Read metadata.json if exists
            metadata_path = session_path / "metadata.json"
            metadata = {}
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except Exception:
                    pass
            
            # Read gal.json if exists to get the main goal
            gal_path = session_path / "gal.json"
            goal = "Unknown Goal"
            if gal_path.exists():
                try:
                    with open(gal_path, 'r', encoding='utf-8') as f:
                        gal_data = json.load(f)
                        goal = gal_data.get("main_goal", "Unknown Goal")
                except Exception:
                    pass
            
            sessions.append({
                "session_id": session_id,
                "name": metadata.get("name", f"Session {session_id[:8]}"),
                "timestamp": metadata.get("created_at", "Unknown"),
                "goal": goal
            })
            
    # Sort by timestamp descending if possible
    sessions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return {"sessions": sessions}


@router.post("/completions")
def chat_completion(request: ChatRequest):
    """
    Handles chat interaction using the context of a specific session.
    """
    session_dir = Path(f"eva_sessions/{request.session_id}")
    
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Compile entire session context into a system prompt
    context_parts = []
    
    # Load GAL
    gal_path = session_dir / "gal.json"
    if gal_path.exists():
        try:
            with open(gal_path, 'r', encoding='utf-8') as f:
                gal_data = json.load(f)
                context_parts.append(f"### Goal Analytical Ledger (GAL):\n{json.dumps(gal_data, indent=2)}")
        except Exception:
            pass
            
    # Load Pipeline State
    state_path = session_dir / "pipeline_state.json"
    if state_path.exists():
         try:
             with open(state_path, 'r', encoding='utf-8') as f:
                 state_data = json.load(f)
                 context_parts.append(f"### Pipeline State:\n{json.dumps(state_data[-1] if isinstance(state_data, list) else state_data, indent=2)}")
         except Exception:
             pass

    # Load findings or visualizations if present
    findings_dir = session_dir / "findings"
    if findings_dir.exists() and findings_dir.is_dir():
         finding_files = list(findings_dir.glob("*.json"))
         if finding_files:
             context_parts.append("### Key Findings Available:")
             for ff in finding_files[:5]: # limit to avoid blowing up context
                 context_parts.append(f"- {ff.name}")

    if not context_parts:
        context_parts.append("This session currently has no active data or pipeline state logged.")

    system_context = "\n\n".join(context_parts)
    
    system_prompt = (
        "You are an expert AI Data Science Assistant embedded within the EVA Analytical OS dashboard.\n"
        "The user is asking questions about a specific data science session. "
        "You have full access to the context of this session below.\n\n"
        "Use this context to answer their questions accurately, clearly, and concisely. "
        "If they ask for insights, refer specifically to the data and goals defined in the context.\n\n"
        "SESSION CONTEXT:\n"
        "===============\n"
        f"{system_context}\n"
        "===============\n"
    )
    
    # Construct LangChain messages
    lc_messages = [SystemMessage(content=system_prompt)]
    
    for msg in request.messages:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role in ["assistant", "ai"]:
            lc_messages.append(AIMessage(content=msg.content))
            
    try:
        # Use the fast reasoning model for interactive chat
        llm = get_llm("fast_reasoning")
        
        # Override to enable streaming technically, though we'll return it all at once for simplicity first 
        # (Streaming via FastAPI involves StreamingResponse, which is doable but complex for MVP)
        result = llm.invoke(lc_messages)
        
        return {
            "role": "assistant",
            "content": result.content
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")
