import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Backend.api.routes import session, chat

app = FastAPI(
    title="EVA Analytical Operating System",
    description="Autonomous Data Science Session Manager API",
    version="1.0.0"
)

# CORS configuration for Frontend/Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router, prefix="/session", tags=["Session"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "EVA is active"}

if __name__ == "__main__":
    import uvicorn
    # Local dev server
    uvicorn.run(app, host="0.0.0.0", port=8000)
