import datetime
from typing import Dict, Optional
from recording_session import RecordingSession, RecordingSessionRole
import threading
import name_generator
from dataclasses import dataclass


@dataclass
class AccessToken:
    token_id: str
    creation_time: datetime.datetime
    session: RecordingSession
    role: RecordingSessionRole


class PersistentStateSingleton:
    def __init__(self):
        self._lock = threading.Lock()
        self._recording_sessions: Dict[str, RecordingSession] = {}

        self._session_tokens: Dict[str, AccessToken] = {}

    # def session_exists(self, session_id) -> bool:
    #     with self._lock:
    #         return session_id in self._recording_sessions.keys()
    #
    # def get_extant_session(self, session_id):
    #     with self._lock:
    #         return self._recording_sessions.get(session_id, None)

    def create_session(self) -> RecordingSession:
        with self._lock:
            new_session_name = name_generator.get_random_name()
            while new_session_name in self._recording_sessions.keys():
                new_session_name = name_generator.get_random_name()
            session = RecordingSession(new_session_name, 42)
            self._recording_sessions[new_session_name] = session
        return session

    def create_access_token(self, role: RecordingSessionRole, recording_session: RecordingSession) -> str:
        with self._lock:
            new_token_id = name_generator.get_random_token()
            while new_token_id in self._session_tokens.keys():
                new_token_id = name_generator.get_random_token()
            self._session_tokens[new_token_id] = AccessToken(
                token_id=new_token_id,
                creation_time=datetime.datetime.now(),
                session=recording_session,
                role=role
            )
        return new_token_id

    def get_session_and_burn_token(self, token_id: str) -> Optional[AccessToken]:
        with self._lock:
            access_token = self._session_tokens.pop(token_id, None)
        # Tokens older than 5 minutes will be invalid
        if access_token is not None and datetime.datetime.now() - access_token.creation_time > datetime.timedelta(minutes=5):
            return access_token
        else:
            return None
