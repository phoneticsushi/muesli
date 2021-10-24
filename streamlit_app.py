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

st.title('Muesli Practice Helper')


def display_audio_clip_with_autoplay_HACK(clip: AudioSegment):
    clip_with_headers = clip.export(format='wav')

    clip_str = "data:audio/wav;base64,%s" % (base64.b64encode(clip_with_headers.read()).decode())
    clip_html = """
                    <audio autoplay="autoplay" controls class="stAudio">
                        <source src="%s" type="audio/wav">
                        Your browser does not support the audio element.
                    </audio>
                """ % clip_str
    st.markdown(clip_html, unsafe_allow_html=True)

def send_balloons_if_lucky():
    if random.randint(0, 100) == 0:
        st.balloons()


# Initialize audio only once per session as it's an expensive operation
def get_audio_handle() -> AudioIO:
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
    if not isinstance(sound, AudioSegment):
        st.warning('display_nonsilence called with non-AudioSegment!')
        return

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
    display_audio_clip_with_autoplay_HACK(last_clip)

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

draw_sidebar_with_preferences()

with st.spinner('Initializing Audio...'):
    aio = get_audio_handle()

toggled = st.button('Toggle Recording...')

sound_status = st.text('Sample Text')  # TODO: refactor this

# Check to see if we have any output from last run
if toggled:
    if aio.is_recording():
        sound_status.text('Checking most recent recording...')
        sound: Optional[AudioSegment] = aio.finish_recording()
        if sound:
            sound_status.text('Splitting most recent recording on silence...')
            display_nonsilence(sound)
            sound_status.text('Recording is ready!')
            send_balloons_if_lucky()
        else:
            sound_status.text('How are you able to see this?')
    else:
        sound_status.text('Recording started...')
        aio.start_recording()

else:
    if aio.is_recording():
        sound_status.text('Recording in progress..')
    else:
        sound_status.text('Not recording')
        # TODO: delay the start recording into a third state?
