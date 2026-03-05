import sys
import traceback
import json
import os
from pathlib import Path
from Backend.orchestrator.pipeline import start_phase_2
from Backend.storage.gal_manager import GALManager

def main():
    sessions_dir = Path('eva_sessions')
    sessions = [d for d in sessions_dir.iterdir() if d.is_dir()]
    if not sessions:
        print('No sessions found.')
        return
    recent_session = sorted(sessions, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    session_id = recent_session.name
    print(f'Using session_id: {session_id}')
    try:
        from Backend.orchestrator.pipeline import start_phase_2
        res = start_phase_2(session_id)
        print(json.dumps(res, indent=2))
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    main()
