from datetime import datetime
from pydub import AudioSegment
import name_generator
import audioplots
import streamlit as st
import time


class AudioClip:
    def __init__(self, audio_segment, selected=False):  # TODO: remove selected when retiring standalone app
        # Set by Recorder on construction
        start = time.time()
        self.name: str = name_generator.get_random_name()
        end = time.time()
        print(f'Time to generate random name: {end - start}')
        self.creation_time: datetime = datetime.now()
        self.audio_segment: AudioSegment = audio_segment

        # Set by Listener
        self.selected: bool = selected

        # Set by this instance when the listener calls for them
        self._waveform_img = None
        self._stft_img = None
        self._split_waveform_img = None
        self._tempo_estimate = None

    def __hash__(self):
        return self.creation_time.__hash__()

    # Ignoring locks to ensure thread safety because this function is idempotent
    # Worst case, multiple listener threads compute the same figures
    def _resolve_clip_statistics(self):
        librosa_clip = None  # Only compute this if necessary

        if self._waveform_img is None:
            if librosa_clip is None:
                librosa_clip = audioplots.audiosegment_to_librosa(self.audio_segment)
            self._waveform_img = audioplots.plot_waveform(librosa_clip, self.audio_segment.frame_rate)

        if self._stft_img is None:
            if librosa_clip is None:
                librosa_clip = audioplots.audiosegment_to_librosa(self.audio_segment)
            self._stft_img = audioplots.plot_stft(librosa_clip, self.audio_segment.frame_rate)

        if self._split_waveform_img is None:
            if librosa_clip is None:
                librosa_clip = audioplots.audiosegment_to_librosa(self.audio_segment)
            self._split_waveform_img = audioplots.plot_split_waveform(librosa_clip, self.audio_segment.frame_rate)

        if not self._tempo_estimate:
            if librosa_clip is None:
                librosa_clip = audioplots.audiosegment_to_librosa(self.audio_segment)
            # TODO: remove hardcoded approximate bpm
            self._tempo_estimate = audioplots.estimate_tempo(librosa_clip, self.audio_segment.frame_rate, 70)

    def get_display_name_markdown(self) -> str:
        if self.selected:
            return f'🔥**{self.name}**🔥'
        else:
            return f'**{self.name}**'

    def draw_clip_deets(self, expand_deets=False):
        self._resolve_clip_statistics()

        with st.expander(label="Pretty Graphs and Deets", expanded=expand_deets):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.caption('Duration')
                st.markdown(f'{len(self.audio_segment) / 1000}s')
                st.caption('Estimated Tempo')
                st.markdown(f'{self._tempo_estimate:.3f} bpm')
                st.caption('Waveform')
                st.image(self._waveform_img)
            with col2:
                st.caption('Average dBFS')
                st.markdown(f'{self.audio_segment.dBFS:.3f}')
                st.caption('Nothing here yet')
                st.markdown(r'¯\\\_(ツ)\_/¯')
                st.caption('Split Waveform')
                st.image(self._split_waveform_img)
            with col3:
                st.caption('Max dBFS')
                st.markdown(f'{self.audio_segment.max_dBFS:.3f}')
                st.caption('Nothing here yet')
                st.markdown(r'¯\\\_(ツ)\_/¯')
                st.caption('STFT')
                st.image(self._stft_img)
