import time

from recording_session import RecordingSession
import layout

import streamlit as st


# TODO: rename to "draw_muesli_viewer"
def run_muesli_listener(recording_session: RecordingSession):
    st.title(f'Muesli Practice Helper')
    draw_and_apply_recording_enable_checkbox(recording_session)

    if recording_session.is_recording_enabled():
        st.error("Recording in progress...")
    elif recording_session.get_number_of_clips() == 0:
        draw_session_connection_section(recording_session)
    else:
        time.sleep(0.5)
        # TODO: replace this with proper signalling
        all_clips = recording_session.get_clips_oldest_to_newest()
        all_clips[0].selected = True  # Mark most recent clip "selected" since the user interacted here
        layout.draw_audio_clips(all_clips)


def draw_session_connection_section(recording_session: RecordingSession):
    st.header('Attach to Another Session')
    st.text_input('Enter the recording session ID:', key='session_to_join')

    session_to_join = st.session_state.get('session_to_join', None)
    # Print nothing if no session is specified
    if session_to_join:
        if recording_session.get_session_id() == session_to_join:
            st.success(f'Joined session "{recording_session.get_session_id()}"')
        else:
            st.error(f'No session exists with ID "{session_to_join}"')


# TODO: probably not the best place for this
# This code isn't terribly threadsafe, but since the app can be modified at any time,
# The only way to know the current state is to refresh
def draw_and_apply_recording_enable_checkbox(recording_session: RecordingSession):
    if st.session_state.get('st_button_start_recording', None):
        recording_session.update_user_enabled_recording_flag(True)
    elif st.session_state.get('st_button_stop_recording', None):
        recording_session.update_user_enabled_recording_flag(False)

    if recording_session.can_enable_recording():
        # Only pay attention to checkbox if it's possible to record - set to False otherwise
        # Only read checkbox state when it's been clicked
        if recording_session.is_recording_enabled():
            st.button(label='Stop Recording', key='st_button_stop_recording')
        else:
            st.button(label='Start Recording', key='st_button_start_recording')
    else:
        # Remove option to disable recording
        st.warning('No microphones are open - select START in the sidebar on the recording device')
        recording_session.update_user_enabled_recording_flag(False)
