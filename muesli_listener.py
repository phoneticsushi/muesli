import time

from recording_session import RecordingSession
import layout

import streamlit as st

def run_muesli_listener(recording_session: RecordingSession):
    st.title(f'Muesli Practice Helper: Listening to "{recording_session.server_id}"')

    recording_session.recording_enabled = st.number_input("Enable recording?")

    if recording_session.recording_enabled:
        st.info("Recording in progress...")
    else:
        time.sleep(0.5)  # wait a half-second for the server to create the clip
        # TODO: replace this with proper signalling
        draw_ui_for_viewing_clips(recording_session)


def draw_ui_for_viewing_clips(recording_session: RecordingSession):
    all_clips = recording_session.get_clips_oldest_to_newest()
    st.write(f'Number of clips: {len(all_clips)}')

    if all_clips:
        # Mark most recent clip "selected" since the user interacted here
        all_clips[0].selected = True

    layout.draw_audio_clips(all_clips)