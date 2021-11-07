import time

from recording_session import RecordingSession
import layout

import streamlit as st


def uptake_checkbox_state_on_next_run():
    st.session_state['should_uptake_checkbox_state'] = True


# TODO: rename to "draw_muesli_viewer"
def run_muesli_listener(recording_session: RecordingSession):
    st.title(f'Muesli Practice Helper')
    num_clips = recording_session.get_number_of_clips()

    cols = st.columns(3)
    with cols[0]:
        st.caption('Session ID')
        st.write(f'"{recording_session.get_server_id()}"')
    with cols[2]:
        st.caption('Refresh')
        st.button('Refresh')

    draw_and_apply_recording_enable_checkbox(recording_session)

    if recording_session.is_recording_enabled():
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


# TODO: probably not the best place for this
# This code isn't terribly threadsafe, but since the app can be modified at any time,
# The only way to know the current state is to refresh
def draw_and_apply_recording_enable_checkbox(recording_session: RecordingSession):
    uptake_checkbox = st.session_state.get('should_uptake_checkbox_state', None)
    st.session_state['should_uptake_checkbox_state'] = False

    if recording_session.can_enable_recording():
        # Only pay attention to checkbox if it's possible to record - set to False otherwise
        if uptake_checkbox:
            recording_session.update_user_enabled_recording_flag(
                st.session_state.get('st.checkbox_enable_recording', None)
            )

        st.checkbox(
            label="Enable Recording",
            key='st.checkbox_enable_recording',
            value=recording_session.is_recording_enabled(),
            on_change=uptake_checkbox_state_on_next_run
        )
    else:
        # Remove option to disable recording
        st.warning('No microphones are open - select START in the sidebar on the recording device')
        recording_session.update_user_enabled_recording_flag(False)
