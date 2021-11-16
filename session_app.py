import random

import streamlit as st

from muesli_landingpage import draw_muesli_landingpage
from recording_session import *
import qrcode

from muesli_viewer import *
from muesli_recorder import *
from persistent_state_singleton import PersistentStateSingleton
from name_generator import get_random_name

@st.experimental_singleton()
def get_persistent_state():
    return PersistentStateSingleton()


def draw_qr_code(url: str):
    img = qrcode.make(url)
    st.image(img.get_image())


def draw_debug_controls(recording_session: RecordingSession, role: RecordingSessionRole):
    st.title('DEBUG Interface')

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


def draw_session_id_section(recording_session: RecordingSession):
    st.title("This Recording Session's ID")
    st.write(recording_session.get_session_id())


# TODO: this
def display_remote_code(recording_session):
    url = f'http://192.168.1.66:8501?token={st.session_state["selected_session"]}'
    draw_qr_code(url)
    if st.button('Return to previous screen, lol'):
        st.session_state['st_button_add_remote'] = False


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


# If client not already bound to a session, try any access token the user may have entered
if 'recording_session' not in st.session_state.keys() and 'recording_session_role' not in st.session_state.keys():
    try_setting_session_from_token_id(st.session_state.get('last_access_token_tried', None))


# If that didn't work, try any session entered as URL parameters:
if 'recording_session' not in st.session_state.keys() and 'recording_session_role' not in st.session_state.keys():
    token_params = st.experimental_get_query_params().get('token', None)
    if token_params:
        # Comes in as list - use the first param specified
        try_setting_session_from_token_id(token_params[0])


recording_session = st.session_state.get('recording_session', None)
recording_role = st.session_state.get('recording_session_role', None)

# If still no session, display the landing page
if recording_session is None or recording_role is None:
    draw_muesli_landingpage()
else:
    print(f'DEBUG: {random.randint(0,100)} about to draw UI for role={recording_role}')
    draw_muesli_viewer(recording_session, recording_role)
    with st.sidebar:
        draw_session_id_section(recording_session)
        run_muesli_recorder(recording_session, recording_role)
        draw_debug_controls(recording_session, recording_role)

# TODO: handle displaying UI for attaching remotes/listeners
# recording_session = None
# session_to_join = st.session_state.get('session_to_join', None)
#
# if session_to_join:
#     recording_session = get_persistent_state().get_extant_session(session_to_join)
#     if recording_session:
#         st.session_state['selected_session'] = session_to_join
#     print(f'DEBUG: session to join {session_to_join}')
#
# # Try connecting to the session we were previously connected to
# if not recording_session:
#     selected_session_id = st.session_state.get('selected_session', None)
#     print(f'DEBUG: try previous {selected_session_id}')
#     if selected_session_id:
#         recording_session = get_persistent_state().get_extant_session(selected_session_id)

# # If that fails, create one
# if not recording_session:
#     new_session_id = get_random_name()
#     st.session_state['selected_session'] = new_session_id
#     recording_session = get_persistent_state().get_or_create_session(new_session_id)
#     print(f'Created new session: "{new_session_id}"')
#
# # Draw UI
# if st.session_state.get('st_button_add_remote'):
#     display_remote_code(recording_session)
# else:
#     run_muesli_listener(recording_session)
#     with st.sidebar:
#         draw_session_id_section(recording_session)
#         run_muesli_recorder(recording_session)
#         draw_debug_controls(recording_session)
