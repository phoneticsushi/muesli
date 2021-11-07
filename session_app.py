import streamlit as st
from recording_session import *

from muesli_listener import *
from muesli_recorder import *


@st.experimental_singleton()
def get_the_only_recording_session():
    return RecordingSession('WUSS POPPIN JIMBO', 42)


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
    st.write(recording_session.get_server_id())

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
    draw_debug_controls(recording_session)
    draw_session_id_section(recording_session)
    run_muesli_recorder(recording_session)
