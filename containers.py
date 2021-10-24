from typing import *
from datetime import datetime
from pydub import AudioSegment
from name_generator import get_random_name


class AudioClip:
    def __init__(self, audio_segment, selected=False):
        self.name: str = get_random_name()
        self.creation_time: datetime = datetime.now()
        self.selected: bool = selected

        self.audio_segment: AudioSegment = audio_segment

    def __hash__(self):
        return self.creation_time.__hash__()

    def get_display_name_markdown(self) -> str:
        if self.selected:
            return f'🔥**{self.name}**🔥'
        else:
            return f'**{self.name}**'
