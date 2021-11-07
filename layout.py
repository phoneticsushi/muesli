from containers import AudioClip
from typing import List
import streamlit as st
import itertools
import base64  # For autoplay hack


def draw_audio_player(clip: AudioClip, autoplay=False):
    cols = st.columns([1, 2])

    with cols[0]:
        st.markdown(f'#### {clip.get_display_name_markdown()}')

    with cols[1]:
        segment_file = clip.audio_segment.export(format='wav')
        if autoplay:
            # FIXME: MASSIVE hack to work around missing autoplay feature in Streamlit
            clip_str = "data:audio/wav;base64,%s" % (base64.b64encode(segment_file.read()).decode())
            clip_html = """
                            <audio autoplay="autoplay" controls style="width: 100%%" class="stAudio">
                                <source src="%s" type="audio/wav">
                                Your browser does not support the audio element.
                            </audio>
                        """ % clip_str
            st.markdown(clip_html, unsafe_allow_html=True)
        else:
            st.audio(segment_file.read())


def draw_audio_clip(clip: AudioClip, auto_show=False):
    draw_audio_player(clip, autoplay=auto_show)
    clip.draw_pretty_graphs(expand=auto_show)
    clip.draw_clip_deets(expand=False)


def draw_audio_clips(audio_clips: List[AudioClip]):
    if audio_clips:
        st.markdown('Latest Clip:')
        draw_audio_clip(audio_clips[0], auto_show=True)

    if len(audio_clips) > 1:
        st.markdown('Other Clips:')
        for clip in itertools.islice(audio_clips, 1, None, 1):
            draw_audio_clip(clip, auto_show=False)


