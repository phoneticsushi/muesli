import streamlit as st
from recording_session import *
from muesli_listener import *
from muesli_recorder import *

@st.experimental_singleton()
def get_the_only_recording_session():
    return RecordingSession('WUSS POPPIN JIMBO', 42)


def run_muesli_role_selection():
    st.title('Muesli Recording Helper: Role Selection')
    left_col, right_col = st.columns(2)

    if left_col.button('Be a Recorder'):
        st.session_state['is_recorder'] = True
        st.experimental_rerun()
    elif right_col.button('Be a Listener'):
        st.session_state['is_listener'] = True
        st.experimental_rerun()
    else:
        st.success('Select a role for this session')
        st.info('Open a new tab to create another session')


# Redirect to Role for this instance

st.set_page_config(
    page_title=None,
    page_icon=None,
    layout='wide',
    initial_sidebar_state='auto',
    menu_items=None
)

is_recorder = st.session_state.get('is_recorder', False)
is_listener = st.session_state.get('is_listener', False)

if is_recorder:
    run_muesli_recorder(get_the_only_recording_session())
elif is_listener:
    run_muesli_listener(get_the_only_recording_session())
else:
    run_muesli_role_selection()
