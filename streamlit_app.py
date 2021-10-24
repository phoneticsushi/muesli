import time

import streamlit as st
import pandas as pd
import numpy as np

import pyaudio
from pydub import AudioSegment, silence

import audio_io
from audio_io import AudioIO

st.title('Muesli Practice Helper')


# Initialize audio only once per session as it's an expensive operation
def get_audio_handle():
    if 'aio' not in st.session_state:
        ctx = {
            # names match pyaudio names
            "frames_per_buffer": 1024,  # Record in chunks of 1024 samples
            "format": pyaudio.paInt16,
            "channels": 2,
            "rate": 44100,  # Record at 44100 samples per second
        }
        st.session_state['aio'] = AudioIO(ctx)
    return st.session_state['aio']


def display_audio_clip(clip: AudioSegment):
    clip_with_headers = clip.export(format='wav')
    st.audio(clip_with_headers.read())


def display_nonsilence(sound: AudioSegment):
    st.text(f'Recording duration: {len(sound) / 1000}s')

    start = time.time()
    all_clips = silence.split_on_silence(sound,
                                         min_silence_len=2000,  # this dude will be modified by the user
                                         silence_thresh=-80,  # FIXME: figure this out
                                         keep_silence=100,
                                         seek_step=1)
    end = time.time()
    st.text(f'Processing time to split on silence: {end - start}s')

    st.text(f'Found {len(all_clips)} separate Clip(s)')

    last_clip = all_clips.pop()
    st.text(f'Last Clip duration: {len(last_clip) / 1000}s')
    display_audio_clip(last_clip)

    if all_clips:
        st.text('Other Clips:')
        for clip in reversed(all_clips):
            display_audio_clip(clip)


def draw_sidebar_with_preferences():
    with st.sidebar:
        st.write('Recording preferences:')
        form = st.form(key='Submit')
        with form:
            min_silence_len_ms = st.number_input(
                label="Minimum Silence Length (ms)",
                min_value=0,
                value=2000,
            )
            silence_thresh_dbfs = st.number_input(
                label="Silence Threshold (dBFS)",
                min_value=-100,
                max_value=3,
                value=-80,
            )
            submitted = st.form_submit_button('Submit')
            st.write(submitted)
            st.write(min_silence_len_ms)
            st.write(silence_thresh_dbfs)

# Set up UI Elements

sound_status = st.text('Initializing Audio...')
aio = get_audio_handle()

draw_sidebar_with_preferences()

# Check to see if we have any output from last run
sound: AudioSegment = aio.finish_recording()
if sound:
    sound_status.text('Checking most recent recording...')
    display_nonsilence(sound)
    sound_status.text('Checking most recent recording...Done!')
    st.button('Start Next Recording...')
else:
    sound_status.text('Recording...')
    aio.start_recording()
    st.button('Finish Recording...')
