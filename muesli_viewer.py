import time

from recording_session import RecordingSession, RecordingSessionRole
import layout

import streamlit as st


def draw_muesli_viewer(recording_session: RecordingSession, role: RecordingSessionRole):
    if role is RecordingSessionRole.AUDIO_SOURCE:
        st.title(f'Muesli Practice Helper')
        draw_and_apply_recording_enable_checkbox(recording_session, True)
    elif role is RecordingSessionRole.REMOTE:
        st.title(f'Muesli (Remote Control)')
        draw_and_apply_recording_enable_checkbox(recording_session, False)
    elif role is RecordingSessionRole.VIEWER:
        st.title(f'Muesli (View Only)')
        st.button('Refresh')  # TODO: move this to a column right of "Start Recording"
        # Intentionally don't draw recording controls

    if recording_session.is_recording_enabled():
        st.error("Recording in progress...")
    else:
        time.sleep(0.5)
        # TODO: replace this with proper signalling
        all_clips = recording_session.get_clips_oldest_to_newest()
        if st.session_state.get('st_button_stop_recording', None):
            # Mark most recent clip "selected" since the user just interacted
            # with the "Stop Recording" button in this session
            all_clips[0].selected = True
        layout.draw_audio_clips(all_clips)


# This code isn't terribly threadsafe, but since the app can be modified at any time,
# The only way to know the current state is to refresh
def draw_and_apply_recording_enable_checkbox(recording_session: RecordingSession, should_allow_further_connections: bool):
    if st.session_state.get('st_button_start_recording', None):
        recording_session.update_user_enabled_recording_flag(True)
    elif st.session_state.get('st_button_stop_recording', None):
        recording_session.update_user_enabled_recording_flag(False)

    if should_allow_further_connections:
        # Draw options to connect more remotes and viewers
        # TODO: probably not the best place for this
        rec_col, remote_col, viewer_col = st.columns([2, 1, 1])
        with rec_col:
            draw_recording_button(recording_session)
        with remote_col:
            st.button('Add Remote...', key='st_button_add_remote')
        with viewer_col:
            st.button('Add Viewer...', key='st_button_add_viewer')
    else:
        # Draw only the recording button by itself
        draw_recording_button(recording_session)


def draw_recording_button(recording_session: RecordingSession):
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
        st.button('Refresh')  # TODO: move this to a column right of "Start Recording"
        recording_session.update_user_enabled_recording_flag(False)
