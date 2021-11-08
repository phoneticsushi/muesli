import streamlit as st
from recording_session import *

from muesli_listener import *
from muesli_recorder import *
from persistent_state_singleton import PersistentStateSingleton
from name_generator import get_random_name

@st.experimental_singleton()
def get_persistent_state():
    return PersistentStateSingleton()


def draw_debug_controls(recording_session: RecordingSession):
    st.title('DEBUG Interface')

    st.caption(f'Open mics in current session')
    st.markdown(recording_session._open_microphones)

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

# Draw Page

st.set_page_config(
    page_title=None,
    page_icon=None,
    layout='wide',
    initial_sidebar_state='auto',
    menu_items=None
)

recording_session = None
session_to_join = st.session_state.get('session_to_join', None)

if session_to_join:
    recording_session = get_persistent_state().get_extant_session(session_to_join)
    if recording_session:
        st.session_state['selected_session'] = session_to_join
    print(f'DEBUG: session to join {session_to_join}')

# Try connecting to the session we were previously connected to
if not recording_session:
    selected_session_id = st.session_state.get('selected_session', None)
    print(f'DEBUG: try previous {selected_session_id}')
    if selected_session_id:
        recording_session = get_persistent_state().get_extant_session(selected_session_id)

# If that fails, create one
if not recording_session:
    new_session_id = get_random_name()
    st.session_state['selected_session'] = new_session_id
    recording_session = get_persistent_state().get_or_create_session(new_session_id)
    print(f'Created new session: "{new_session_id}"')

# Draw UI
run_muesli_listener(recording_session)
with st.sidebar:
    draw_debug_controls(recording_session)
    draw_session_id_section(recording_session)
    run_muesli_recorder(recording_session)
