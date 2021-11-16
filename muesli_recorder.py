import streamlit as st

import numpy as np

import pydub
from matplotlib import pyplot as plt

import queue

import threading
import time

from recording_session import RecordingSession, RecordingSessionRole

from streamlit_webrtc import (
    RTCConfiguration,
    WebRtcMode,
    webrtc_streamer,
)

""" Places this instance into Recording Mode
"""
def run_muesli_recorder(recording_session: RecordingSession, role: RecordingSessionRole):
    if role is not RecordingSessionRole.AUDIO_SOURCE:
        st.title('Microphone Disabled')
        st.info('Any microphones must be connected the device that created the recording session')
        return


    # TODO: move these?
    # Use Google STUN server
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    # end TODO section

    st.title(f'Enable/Disable Microphone')

    webrtc_ctx = webrtc_streamer(
        key="sendonly-audio",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=25600,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"audio": True},
    )

    if webrtc_ctx.audio_receiver:
        st.error('Microphone is open...')
        if not st.session_state.get('audio_processing_thread_active', False):
            # Start a thread to process the audio
            print('DEBUG: starting audio processing thread')
            st.session_state['audio_processing_thread_active'] = True
            processing_thread = threading.Thread(target=run_audio_processing_loop, args=[webrtc_ctx, recording_session], daemon=True)
            st.report_thread.add_report_ctx(processing_thread)
            processing_thread.start()
    else:
        st.info('Click START to open the microphone on this device.')
    st.write('The microphone will remain open until you click STOP.')

    st.write('You can use the "Enable Recording" checkbox on the right to start and stop recording.')


def run_audio_processing_loop(webrtc_ctx, recording_session: RecordingSession):
    # TODO: refactor where sound_bytes lives
    sound_bytes = bytearray()

    silent_frames_required_to_save_clip = 4 * 50  # TODO: remove hardcoded 4 seconds

    consecutive_silent_frames = 0
    total_frames_recorded = 0
    total_frames_skipped = 0
    last_frame_was_recording: bool = False

    if not webrtc_ctx.audio_receiver:
        print('DEBUG: audio receiver inactive; exiting processing thread...')
        st.session_state['audio_processing_thread_active'] = False
        return

    recording_session.report_microphone_open()
    while st.session_state.get('audio_processing_thread_active', False):
        try:
            audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=2)
        except queue.Empty:
            print("WARNING: Queue is empty. Abort.")
            break

        for audio_frame in audio_frames:
            if recording_session.is_recording_enabled():
                total_frames_recorded = total_frames_recorded + 1
                np_frame = audio_frame.to_ndarray()
                sound_bytes.extend(np_frame.tobytes())

                if np.amax(np_frame) > 2000:  # TODO: replace magic number
                    # This frame is silence
                    consecutive_silent_frames = 0
                else:
                    consecutive_silent_frames = consecutive_silent_frames + 1
                    if consecutive_silent_frames == silent_frames_required_to_save_clip:
                        save_audio_buffer_to_recording_session(recording_session, sound_bytes, consecutive_silent_frames, audio_frame)
                        sound_bytes = bytearray()
                        consecutive_silent_frames = 0

                last_frame_was_recording = True
            else:  # Recording disabled
                if last_frame_was_recording:
                    save_audio_buffer_to_recording_session(recording_session, sound_bytes, consecutive_silent_frames, audio_frame)
                    sound_bytes = bytearray()  # TODO: move this into above function somehow?

                total_frames_skipped = total_frames_skipped + 1
                consecutive_silent_frames = 0
                last_frame_was_recording = False

            # TODO: remove debug code
            # if (total_frames_recorded + total_frames_skipped) % 50 == 0:
            #     print(f'DEBUG: REC={recording_session.is_recording_enabled()} | LAST={last_frame_was_recording} | consecutive_silent={consecutive_silent_frames} | silent_required_for_clip={silent_frames_required_to_save_clip} | total_recorded={total_frames_recorded} | total_skipped={total_frames_skipped}')

    print('DEBUG: Loop terminated - exiting audio processing thread')
    st.session_state['audio_processing_thread_active'] = False
    # TODO: due to when this thread exits, this isn't updated in a timely manner
    #   The instance whose microphone was closed tends to miss the update
    recording_session.report_microphone_closed()


# audio_frame is for metadata only - TODO: refactor this
def save_audio_buffer_to_recording_session(recording_session: RecordingSession, sound_buffer, frames_to_trim_from_end, audio_frame) -> None:
    # TODO: fix trimming!
    #print(f'frames={frames_to_trim_from_end} | sample_rate={audio_frame.sample_rate} | buffer_len={len(sound_buffer)}')
    #samples_to_trim_from_end = frames_to_trim_from_end * audio_frame.sample_rate
    #trimmed_sound_buffer = bytes(sound_buffer[:len(sound_buffer) - samples_to_trim_from_end])
    #print(f'trimmed_len={len(trimmed_sound_buffer)}')
    trimmed_sound_buffer = bytes(sound_buffer)  #trimming disabled until I do math properly

    if trimmed_sound_buffer:
        start = time.time()
        audio_segment = pydub.AudioSegment(
            data=trimmed_sound_buffer,
            sample_width=audio_frame.format.bytes,
            frame_rate=audio_frame.sample_rate,
            channels=len(audio_frame.layout.channels),
        )
        recording_session.append_segment_as_clip(audio_segment)
        end = time.time()
        print(f'DEBUG: Appended AudioSegment to session | buffer_len={len(sound_buffer)} | recording len={len(audio_segment)} | wall_time={end-start}')
    else:
        print('WARNING: Sound buffer has no length!')
