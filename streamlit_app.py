import collections
import itertools
import time
import random
from typing import Optional

import streamlit as st
import numpy as np

import pyaudio
from pydub import AudioSegment, silence

from audio_io import AudioIO

from audioplots import *
from containers import *
from layout import *

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


def add_sound_to_clips(sound: AudioSegment):
    if not isinstance(sound, AudioSegment):
        st.warning('display_nonsilence called with non-AudioSegment!')
        return

    with st.spinner('Splitting on silence...'):
        start = time.time()
        current_segments = silence.split_on_silence(sound,
                                                    min_silence_len=2000,  # this dude will be modified by the user
                                                    silence_thresh=sound.dBFS-16,  # FIXME: does this work?
                                                    keep_silence=100,
                                                    seek_step=1)
        end = time.time()

    cols = st.columns(3)
    with cols[0]:
        st.caption('Recording time')
        st.markdown(f'{len(sound) / 1000}s')
    with cols[1]:
        st.caption('Processing Time')
        st.markdown(f'{end - start:.3f}s')
    with cols[2]:
        st.caption('New Clips Found')
        st.markdown(len(current_segments))

    all_clips = st.session_state['all_clips']

    with st.spinner('Creating clips...'):
        if len(current_segments) > 1:
            for segment in current_segments[:-1]:
                all_clips.appendleft(AudioClip(audio_segment=segment, selected=False))

        if len(current_segments) > 0:
            all_clips.appendleft(AudioClip(audio_segment=current_segments[-1], selected=True))


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
            approximate_bpm = st.number_input(
                label="Approximate Tempo (BPM; for tempo estimation)",
                min_value=0,
                max_value=300,
                value=100,
            )
            submitted = st.form_submit_button('Submit')
            st.write(submitted)
            st.write(min_silence_len_s)
            st.write(silence_thresh_dbfs)

# Set up UI Elements

if 'all_clips' not in st.session_state:
    st.session_state['all_clips'] = collections.deque(maxlen=100)  # TODO: remove maxLen?

st.set_page_config(
    page_title=None,
    page_icon=None,
    layout='wide',
    initial_sidebar_state='auto',
    menu_items=None
)

st.title('Muesli Practice Helper')

#draw_sidebar_with_preferences()

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
            add_sound_to_clips(sound)
            sound_status.markdown('Recording is ready!')
            send_balloons_if_lucky()
            draw_audio_clips(st.session_state['all_clips'])
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
        draw_audio_clips(st.session_state['all_clips'])
