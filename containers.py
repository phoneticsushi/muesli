from datetime import datetime
from pydub import AudioSegment
from name_generator import get_random_name
import audioplots


class AudioClip:
    def __init__(self, audio_segment, selected=False):
        self.name: str = get_random_name()
        self.creation_time: datetime = datetime.now()
        self.selected: bool = selected

        self.audio_segment: AudioSegment = audio_segment

        librosa_clip = audioplots.audiosegment_to_librosa(audio_segment)
        # TODO: remove hardcoded sample rate
        self.waveform_fig = audioplots.plot_waveform(librosa_clip, 44100)
        self.stft_fig = audioplots.plot_stft(librosa_clip, 44100)

    def __hash__(self):
        return self.creation_time.__hash__()

    def get_display_name_markdown(self) -> str:
        if self.selected:
            return f'🔥**{self.name}**🔥'
        else:
            return f'**{self.name}**'
