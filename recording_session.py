import collections
import threading
from typing import *
from containers import *
import streamlit as st


# All functions of this class must be threadsafe
class RecordingSession:
    def __init__(self, server_id, max_recordings):
        self._server_id = server_id

        self._recordings: collections.deque[AudioClip] = collections.deque(maxlen=max_recordings)

        # The recorder will toss out all audio when these are Falsey

        self._user_enabled_recording: bool = False  # TODO: check this value for thread safety?
        self._open_microphones: int = 0
        self._lock_open_microphones = threading.Lock()

    def get_server_id(self):
        return self._server_id

    # TODO: will we regret foregoing thread safety?
    # This is accessed in the audio processing loop
    def is_recording_enabled(self):
        return bool(self._user_enabled_recording and self._open_microphones)  # NoneType -> False

    def can_enable_recording(self):
        return self._open_microphones > 0

    def update_user_enabled_recording_flag(self, update):
        self._user_enabled_recording = update

    # Deques are thread-safe for single-append and read operations,
    # so no locking is needed here
    def append_segment_as_clip(self, segment: AudioSegment):
        self._recordings.appendleft(AudioClip(segment))

    # Return shallow copy as list to prevent caller's operations
    # from accidentally modifying _recordings
    # TODO: this is probably not necessary
    def get_clips_oldest_to_newest(self):
        return list(self._recordings)

    def get_number_of_clips(self):
        return len(self._recordings)

    def report_microphone_open(self):
        with self._lock_open_microphones:
            self._open_microphones += 1

    def report_microphone_closed(self):
        with self._lock_open_microphones:
            self._open_microphones -= 1
            # TODO: move this elsewhere?
            if self._open_microphones == 0:
                self._user_enabled_recording = False
