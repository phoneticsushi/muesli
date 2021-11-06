import streamlit as st
from recording_session import *

from muesli_listener import *
from muesli_recorder import *
import gc


@st.experimental_singleton()
def get_the_only_recording_session():
    return RecordingSession('WUSS POPPIN JIMBO', 42)


def draw_debug_controls():
    st.title('DEBUG Controls')
    if st.button("DEBUG: Clear all Recordings"):
        get_the_only_recording_session()._recordings.clear()

    if st.button('DEBUG: Run Garbage Collection'):
        gc.collect()


def draw_session_id_section(recording_session: RecordingSession):
    st.title("This Recording Session's ID")
    st.write(recording_session.server_id)


def draw_session_connection_section():
    st.title('Attach to Another Session')
    # TODO: NYI
    st.text_input('Enter the recording session ID:', key='session_to_join')

    session_to_join = st.session_state.get('session_to_join', None)
    if session_to_join:
        # TODO: support multiple sessions
        st.error(f"Can't join session '{session_to_join}' - multi-session support isn't implemented yet")


# Draw Page

st.set_page_config(
    page_title=None,
    page_icon=None,
    layout='wide',
    initial_sidebar_state='auto',
    menu_items=None
)

recording_session = get_the_only_recording_session()

run_muesli_listener(recording_session)
with st.sidebar:
    draw_debug_controls()
    run_muesli_recorder(recording_session)
    draw_session_id_section(recording_session)
    draw_session_connection_section()
