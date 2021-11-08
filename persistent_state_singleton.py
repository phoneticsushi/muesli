from typing import Dict
from recording_session import RecordingSession


class PersistentStateSingleton:
    def __init__(self):
        self._recording_sessions: Dict[RecordingSession] = {}

    def session_exists(self, session_id):
        return session_id in self._recording_sessions.keys()

    def get_extant_session(self, session_id):
        return self._recording_sessions.get(session_id, None)

    def get_or_create_session(self, session_id):
        session = self.get_extant_session(session_id)
        if session is None:
            session = RecordingSession(session_id, 42)
            self._recording_sessions[session_id] = session
        return session
