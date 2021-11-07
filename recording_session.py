import collections
import threading
from typing import *
from containers import *


class RecordingSession:
    def __init__(self, server_id, max_recordings):
        self.server_id = server_id
        # Set by the listener.  The recorder will toss out all audio when this is False
        self.recording_enabled: bool = False

        self._recordings: collections.deque[AudioClip] = collections.deque(maxlen=max_recordings)

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
