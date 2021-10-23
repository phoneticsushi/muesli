import threading
from typing import *

import pyaudio
from pydub import AudioSegment


class AudioIO:
    def __init__(self, ctx):
        self.p = pyaudio.PyAudio()  # Create an interface to PortAudio
        self.ctx = ctx

        self.in_stream = self.p.open(start=False, input=True, **self.ctx)
        self.out_stream = self.p.open(start=False, output=True, **self.ctx)

        self.recording_thread = None
        self.recording_buffer = None  # managed by _record_audio_thread
        self.should_record = False

    def __del__(self):
        self.in_stream.close()
        self.out_stream.close()
        # Terminate the PortAudio interface
        self.p.terminate()

    def is_recording(self) -> bool:
        if self.recording_thread is not None:
            return self.recording_thread.is_alive()
        else:
            return False

    def start_recording(self):
        if self.recording_thread:
            print('DEBUG: start_recording called but already recording')
            return False

        self.recording_thread = threading.Thread(target=self._record_audio_thread, daemon=True)
        self.should_record = True
        self.recording_thread.start()
        return True

    def finish_recording(self) -> Optional[AudioSegment]:
        if not self.recording_thread:
            print('DEBUG: finish_recording called but not recording')
            return None

        self.should_record = False
        self.recording_thread.join()
        self.recording_thread = None

        # FIXME: remove hardcoded sample_width
        return AudioSegment(self.recording_buffer, sample_width=2, channels=self.ctx['channels'], frame_rate=self.ctx['rate'])

    def play_audio(self, segment: AudioSegment):
        self.out_stream.start_stream()
        self.out_stream.write(bytes(segment.raw_data))
        self.out_stream.stop_stream()

    def _record_audio_thread(self):
        self.recording_buffer = bytearray()
        self.in_stream.start_stream()
        while True:
            self.recording_buffer += self.in_stream.read(self.ctx['frames_per_buffer'])
            if not self.should_record:
                print('DEBUG: Exiting Recording Thread')
                return
