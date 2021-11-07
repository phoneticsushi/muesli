import time

from recording_session import RecordingSession
import layout

import streamlit as st

# TODO: rename to "draw_muesli_viewer"
def run_muesli_listener(recording_session: RecordingSession):
    st.title(f'Muesli Practice Helper')
    num_clips = recording_session.get_number_of_clips()

    cols = st.columns(3)
    with cols[0]:
        st.caption('Session ID')
        st.write(f'"{recording_session.server_id}"')
    with cols[2]:
        st.caption('Refresh')
        st.button('Refresh')

    recording_session.recording_enabled = st.checkbox("Enable Recording")
    if recording_session.recording_enabled:
        st.info("Recording in progress...")
    elif num_clips == 0:
        draw_session_connection_section()
    else:
        time.sleep(0.5)
        # TODO: replace this with proper signalling
        all_clips = recording_session.get_clips_oldest_to_newest()
        num_clips = len(all_clips)
        all_clips[0].selected = True  # Mark most recent clip "selected" since the user interacted here
        layout.draw_audio_clips(all_clips)

    # Fill in number of clips after rendering clips to make sure all_clips is updated correctly
    with cols[1]:
        st.caption('Number of Clips')
        st.markdown(num_clips)


def draw_session_connection_section():
    st.header('Attach to Another Session')
    st.text_input('Enter the recording session ID:', key='session_to_join')

    session_to_join = st.session_state.get('session_to_join', None)
    if session_to_join:
        # TODO: support multiple sessions
        st.error(f"Can't join session '{session_to_join}' - multi-session support isn't implemented yet")
