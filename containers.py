from datetime import datetime
from pydub import AudioSegment
from name_generator import get_random_name
import audioplots
import streamlit as st


class AudioClip:
    def __init__(self, audio_segment, selected=False):
        self.name: str = get_random_name()
        self.creation_time: datetime = datetime.now()
        self.selected: bool = selected

        self.audio_segment: AudioSegment = audio_segment

        librosa_clip = audioplots.audiosegment_to_librosa(audio_segment)
        self.waveform_fig = audioplots.plot_waveform(librosa_clip, self.audio_segment.frame_rate)
        self.stft_fig = audioplots.plot_stft(librosa_clip, self.audio_segment.frame_rate)
        self.split_waveform_fig = audioplots.plot_split_waveform(librosa_clip, self.audio_segment.frame_rate)

        # TODO: remove hardcoded approximate bpm
        self.tempo_estimate = audioplots.estimate_tempo(librosa_clip, self.audio_segment.frame_rate, 70)

    def __hash__(self):
        return self.creation_time.__hash__()

    def get_display_name_markdown(self) -> str:
        if self.selected:
            return f'🔥**{self.name}**🔥'
        else:
            return f'**{self.name}**'

    def draw_clip_deets(self, expand_deets=False):
        with st.expander(label="Pretty Graphs and Deets", expanded=expand_deets):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.caption('Duration')
                st.markdown(f'{len(self.audio_segment) / 1000}s')
                st.caption('Estimated Tempo')
                st.markdown(f'{self.tempo_estimate:.3f} bpm')
                st.caption('Waveform')
                st.pyplot(self.waveform_fig)
            with col2:
                st.caption('Average dBFS')
                st.markdown(f'{self.audio_segment.dBFS:.3f}')
                st.caption('Nothing here yet')
                st.markdown(r'¯\\\_(ツ)\_/¯')
                st.caption('Split Waveform')
                st.pyplot(self.split_waveform_fig)
            with col3:
                st.caption('Max dBFS')
                st.markdown(f'{self.audio_segment.max_dBFS:.3f}')
                st.caption('Nothing here yet')
                st.markdown(r'¯\\\_(ツ)\_/¯')
                st.caption('STFT')
                st.pyplot(self.stft_fig)
