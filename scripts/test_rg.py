import sys
import json
import asyncio

# Setup path so Backend is importable
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Backend.api.routes.session import execute_rg

session_id = "b843efde-9897-42ca-b065-8b8b10c877d3"
print(f"Executing RG for session: {session_id} in lite mode...")

try:
    response = execute_rg(session_id, rules_mode="lite")
    print("\n--- RG Result ---")
    print(response.model_dump_json(indent=2))
except Exception as e:
    print(f"Error executing RG: {e}")
