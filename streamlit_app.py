from tempfile import TemporaryFile
import time
import random
from typing import Optional
import base64  # For autoplay hack

import streamlit as st
import pandas as pd
import numpy as np

import pyaudio
from pydub import AudioSegment, silence

import audio_io
from audio_io import AudioIO

from audioplots import *

ctx = {
    # names match pyaudio names
    "frames_per_buffer": 1024,  # Record in chunks of 1024 samples
    "format": pyaudio.paInt16,
    "channels": 2,
    "rate": 44100,  # Record at 44100 samples per second
}


def send_balloons_if_lucky():
    if random.randint(0, 100) == 0:
        st.balloons()


# Initialize audio only once per session as it's an expensive operation
def get_audio_handle() -> AudioIO:
    if 'aio' not in st.session_state:
        st.session_state['aio'] = AudioIO(ctx)
    return st.session_state['aio']


def draw_clip_plots(clip: AudioSegment, show_graphs=False):
    with st.expander(label="Pretty Graphs", expanded=show_graphs):
        wave_col, stft_col, unused_col = st.columns(3)

        # Convert clip to librosa format to appease librosa
        librosa_clip = np.frombuffer(clip.raw_data, dtype=np.int16)
        librosa_clip = librosa_clip / 32768  # Convert values form int16 to normalized float

        with wave_col:
            st.caption('Duration')
            st.markdown(f'{len(clip) / 1000}s')
            st.caption('Waveform')
            st.pyplot(plot_waveform(librosa_clip, ctx['rate']))
        with stft_col:
            st.caption('Average dBFS')
            st.markdown(clip.dBFS)
            st.caption('STFT')
            st.pyplot(plot_stft(librosa_clip, ctx['rate']))
        with unused_col:
            st.caption('Max dBFS')
            st.markdown(clip.max_dBFS)
            st.caption('Nothing here yet')
            # TODO: put something here?


def draw_audio_player(clip: AudioSegment, autoplay=False):
    clip_file = clip.export(format='wav')
    if autoplay:
        # MASSIVE hack to work around missing autoplay feature in Streamlit
        clip_str = "data:audio/wav;base64,%s" % (base64.b64encode(clip_file.read()).decode())
        clip_html = """
                        <audio autoplay="autoplay" controls class="stAudio">
                            <source src="%s" type="audio/wav">
                            Your browser does not support the audio element.
                        </audio>
                    """ % clip_str
        st.markdown(clip_html, unsafe_allow_html=True)
    else:
        st.audio(clip_file.read())


def display_nonsilence(sound: AudioSegment):
    if not isinstance(sound, AudioSegment):
        st.warning('display_nonsilence called with non-AudioSegment!')
        return

    cols = st.columns(3)

    with cols[0]:
        st.caption('Recording time')
        st.markdown(f'{len(sound) / 1000}s')

    with st.spinner('Splitting on silence...'):
        start = time.time()
        all_clips = silence.split_on_silence(sound,
                                             min_silence_len=2000,  # this dude will be modified by the user
                                             silence_thresh=-80,  # FIXME: figure this out
                                             keep_silence=100,
                                             seek_step=1)
        end = time.time()

    with cols[1]:
        st.caption('Processing Time')
        st.markdown(f'{end - start}s')

    with cols[2]:
        st.caption('Clips Found')
        st.markdown(len(all_clips))

    if all_clips:
        last_clip = all_clips.pop()
        st.markdown('Last Clip:')
        draw_audio_player(last_clip, autoplay=True)
        draw_clip_plots(last_clip, show_graphs=True)

    if all_clips:
        st.markdown('Other Clips:')
        for clip in reversed(all_clips):
            draw_audio_player(clip, autoplay=False)
            draw_clip_plots(clip, show_graphs=False)


def draw_sidebar_with_preferences():
    with st.sidebar:
        st.write('Recording preferences:')
        form = st.form(key='Submit')
        with form:
            min_silence_len_s = st.number_input(
                label="Minimum Silence Length (s)",
                min_value=0,
                value=2,
            )
            silence_thresh_dbfs = st.number_input(
                label="Silence Threshold (dBFS)",
                min_value=-200,
                max_value=3,
                value=-80,
            )
            submitted = st.form_submit_button('Submit')
            st.write(submitted)
            st.write(min_silence_len_s)
            st.write(silence_thresh_dbfs)

# Set up UI Elements

st.title('Muesli Practice Helper')

draw_sidebar_with_preferences()

with st.spinner('Initializing Audio...'):
    aio = get_audio_handle()

toggled = st.button('Toggle Recording...')

sound_status = st.markdown('Sample Text')  # TODO: refactor this

# Check to see if we have any output from last run
if toggled:
    if aio.is_recording():
        sound_status.markdown('Checking most recent recording...')
        sound: Optional[AudioSegment] = aio.finish_recording()
        if sound:
            sound_status.markdown('Splitting most recent recording on silence...')
            display_nonsilence(sound)
            sound_status.markdown('Recording is ready!')
            send_balloons_if_lucky()
        else:
            sound_status.markdown('How are you able to see this?')
    else:
        sound_status.markdown('Recording started...')
        aio.start_recording()

else:
    if aio.is_recording():
        sound_status.markdown('Recording in progress..')
    else:
        sound_status.markdown('Not recording')
