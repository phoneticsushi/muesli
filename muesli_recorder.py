import streamlit as st
import numpy as np

import pydub
from matplotlib import pyplot as plt

import logging
import queue

import gc
import time

from recording_session import RecordingSession

from streamlit_webrtc import (
    RTCConfiguration,
    WebRtcMode,
    webrtc_streamer,
)

""" Places this instance into Recording Mode
"""
def run_muesli_recorder(recording_session: RecordingSession):
    # TODO: move these?
    # Use Google STUN server
    RTC_CONFIGURATION = RTCConfiguration(
        {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )
    logger = logging.getLogger(__name__)

    st.title(f'Muesli Practice Helper: Recording for "{recording_session.server_id}"')

    # TODO: remove debugs
    if st.button("DEBUG: clear cache"):
        recording_session._recordings.clear()

    if st.button('DEBUG: Collect Garbage'):
        gc.collect()

    webrtc_ctx = webrtc_streamer(
        key="sendonly-audio",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=25600,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"audio": True},
    )

    silent_frames_required_to_save_clip = 4 * 50  # TODO: remove hardcoded 4 seconds

    consecutive_silent_frames = 0
    total_frames_recorded = 0
    total_frames_skipped = 0
    last_frame_was_recording: bool = False

    # TODO: refactor where sound_bytes lives
    sound_bytes = bytearray()

    if webrtc_ctx.audio_receiver:
        st.error('Microphone is open...')
    else:
        st.success('Click START to open the microphone')
    st.info('The microphone will remain open until you click STOP, but audio will only be saved when the listening session requests it.')

    # Event loop
    while True:
        if webrtc_ctx.audio_receiver:
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=2)
            except queue.Empty:
                logger.warning("Queue is empty. Abort.")
                break

            for audio_frame in audio_frames:
                if recording_session.recording_enabled:
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

                if (total_frames_recorded + total_frames_skipped) % 50 == 0:
                    print(f'DEBUG: REC={recording_session.recording_enabled} | LAST={last_frame_was_recording} | consecutive_silent={consecutive_silent_frames} | silent_required_for_clip={silent_frames_required_to_save_clip} | total_recorded={total_frames_recorded} | total_skipped={total_frames_skipped}')
        else:
            logger.warning("Break out of loop, lol")
            break


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

        # TODO: remove this code
        segment_file = audio_segment.export(format='wav')
        plt.plot(audio_segment.get_array_of_samples())
        st.pyplot(plt.gcf())
        plt.clf()
        st.audio(segment_file.read())
        # END TODO
    else:
        print('WARNING: Sound buffer has no length!')


            # if len(audio_segment) > 0:
            #     if sound_window_buffer is None:
            #         sound_window_buffer = pydub.AudioSegment.silent(
            #             duration=sound_window_len
            #         )
            #
            #     sound_window_buffer += audio_segment
            #     if len(sound_window_buffer) > sound_window_len:
            #         sound_window_buffer = sound_window_buffer[-sound_window_len:]
            #
            # if sound_window_buffer:
            #     # Ref: https://own-search-and-study.xyz/2017/10/27/python%E3%82%92%E4%BD%BF%E3%81%A3%E3%81%A6%E9%9F%B3%E5%A3%B0%E3%83%87%E3%83%BC%E3%82%BF%E3%81%8B%E3%82%89%E3%82%B9%E3%83%9A%E3%82%AF%E3%83%88%E3%83%AD%E3%82%B0%E3%83%A9%E3%83%A0%E3%82%92%E4%BD%9C/  # noqa
            #     sound_window_buffer = sound_window_buffer.set_channels(
            #         1
            #     )  # Stereo to mono
            #     sample = np.array(sound_window_buffer.get_array_of_samples())
            #
            #     ax_time.cla()
            #     times = (np.arange(-len(sample), 0)) / sound_window_buffer.frame_rate
            #     ax_time.plot(times, sample)
            #     ax_time.set_xlabel("Time")
            #     ax_time.set_ylabel("Magnitude")
            #
            #     spec = np.fft.fft(sample)
            #     freq = np.fft.fftfreq(sample.shape[0], 1.0 / audio_segment.frame_rate)
            #     freq = freq[: int(freq.shape[0] / 2)]
            #     spec = spec[: int(spec.shape[0] / 2)]
            #     spec[0] = spec[0] / 2
            #
            #     ax_freq.cla()
            #     ax_freq.plot(freq, np.abs(spec))
            #     ax_freq.set_xlabel("Frequency")
            #     ax_freq.set_yscale("log")
            #     ax_freq.set_ylabel("Magnitude")
            #
            #     fig_place.pyplot(fig)