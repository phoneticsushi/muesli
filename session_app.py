import random

import streamlit as st

from muesli_landingpage import draw_muesli_landingpage
from recording_session import *

from muesli_viewer import *
from muesli_recorder import *
from muesli_qr_page import *
from persistent_state_singleton import PersistentStateSingleton
from name_generator import get_random_name


def draw_debug_controls(recording_session: RecordingSession, role: RecordingSessionRole):
    st.title('DEBUG Interface')

    st.title("This Recording Session's ID")
    st.write(recording_session.get_session_id())

    st.caption("This Client's Role")
    st.write(role)

    st.caption(f'Open mics in current session')
    st.markdown(recording_session._open_microphones)

    st.caption(f'Number of clips in current session')
    st.markdown(recording_session.get_number_of_clips())

# TODO:: no longer a thing
    st.caption(f'Used Enabled Recording (local)')
    st.write(st.session_state.get('st_checkbox_enable_recording', None))

    st.caption(f'Used Enabled Recording (global)')
    st.write(recording_session._user_enabled_recording)

    st.caption(f'Debug Actions')
    if st.button("Clear Recordings in Current Session"):
        recording_session._recordings.clear()

    st.caption('Memes')
    st.video('https://www.youtube.com/watch?v=HaF-nRS_CWM')


def draw_remote_control_help():
    st.title('Remote Control')
    # TODO: just move the buttons to this section?
    # TODO: None of this is correct anymore
    st.write(f"To use this device's microphone but control recording from another device:")
    st.markdown('1. Press START on this device\n'
                '2. Navigate to this page from another device\n'
                f'3. Enter the session ID "{recording_session.get_session_id()}" on the other device\n'
                '4. Use the "Enable Recording" checkbox on the other device')


def try_setting_session_from_token_id(access_token_id: str):
    if access_token_id:
        access_token = get_persistent_state().get_session_and_burn_token(access_token_id)

        if access_token:
            print(f'DEBUG: found session for token "{access_token_id}" | session_id={access_token.session.get_session_id()} | role={access_token.role}')
            st.session_state['recording_session'] = access_token.session
            st.session_state['recording_session_role'] = access_token.role


# Draw Page

st.set_page_config(
    page_title=None,
    page_icon=None,
    layout='wide',
    initial_sidebar_state='auto',
    menu_items=None
)

# Check to see if the "create new session" button was pressed
if st.session_state.get('should_create_new_session', None):
    st.session_state['recording_session'] = get_persistent_state().create_session()
    st.session_state['recording_session_role'] = RecordingSessionRole.AUDIO_SOURCE


# Try any session entered as URL parameters first, otherwise try anything the user may have entered:
if 'recording_session' not in st.session_state.keys() and 'recording_session_role' not in st.session_state.keys():
    token_params = st.experimental_get_query_params().get('token', None)
    if token_params:
        # Comes in as list - use the first param specified
        st.session_state['last_access_token_tried'] = token_params[0]
        st.experimental_set_query_params()
    try_setting_session_from_token_id(st.session_state.get('last_access_token_tried', None))


recording_session = st.session_state.get('recording_session', None)
recording_role = st.session_state.get('recording_session_role', None)

# If still no session, display the landing page
if recording_session is None or recording_role is None:
    draw_muesli_landingpage()
# Check to see if the "add remote / add viewer" buttons were pressed
elif st.session_state.get('st_button_add_remote', None):
    draw_muesli_qr_page(recording_session, RecordingSessionRole.REMOTE)
elif st.session_state.get('st_button_add_viewer', None):
    draw_muesli_qr_page(recording_session, RecordingSessionRole.VIEWER)
# If not in some unusual mode, draw the main UI
else:
    print(f'DEBUG: {random.randint(0,100)} about to draw UI for role={recording_role}')
    draw_muesli_viewer(recording_session, recording_role)
    with st.sidebar:
        run_muesli_recorder(recording_session, recording_role)
        draw_debug_controls(recording_session, recording_role)
