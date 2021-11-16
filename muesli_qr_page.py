import streamlit as st
import qrcode
from recording_session import RecordingSession, RecordingSessionRole
from persistent_state_singleton import get_persistent_state


def draw_qr_code(url: str):
    img = qrcode.make(url)
    st.image(img.get_image())


def draw_remote_code(access_token_id):
    # TODO: find a way to get the URL of the current server
    #  from within Streamlit
    url = f'https://share.streamlit.io/phoneticsushi/muesli/cloud-deploy/session_app.py?token={access_token_id}'

    st.header('To attach a device:')
    st.write('Scan this QR code on another device:')
    draw_qr_code(url)
    st.header('Or:')
    st.write('Enter the following token on another device:')
    st.title(access_token_id)


def draw_muesli_qr_page(recording_session: RecordingSession, role_for_connecting_client: RecordingSessionRole):
    access_token_id = get_persistent_state().create_access_token(role_for_connecting_client, recording_session)

    st.title('Muesli (Attach a Device)')

    if role_for_connecting_client is RecordingSessionRole.REMOTE:
        st.warning("You're about to connect a Remote to this session.  The remote will be able to start and stop "
                 "recording clips using this device's microphone, but only when the microphone on this device "
                 "is open.")
    elif role_for_connecting_client is RecordingSessionRole.VIEWER:
        st.success("You're about to connect a Viewer to this session.  The Viewer will be able to listen to "
                   "any clips in this session, but they won't be able to control recording.")
    else:
        st.info("If you can see this, it means there's an error in the code.  Who knows what will happen?")

    st.info('This access token will expire in five minutes or after the first use.')
    if st.button('Return to the previous screen'):
        st.session_state['st_button_add_remote'] = False
        st.session_state['st_button_add_viewer'] = False

    draw_remote_code(access_token_id)
