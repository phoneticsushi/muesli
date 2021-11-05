import io

import librosa
import matplotlib
import numpy as np
from librosa import display
from matplotlib import pyplot as plt, figure

from containers import AudioSegment


def audiosegment_to_librosa(segment: AudioSegment):
    segment_file = segment.export(format='wav')
    y, sr = librosa.load(path=segment_file, sr=None)
    return y


# Lift code from Streamlit's pyplot.py so we can store images instead of figures and avoid wasting memory
def get_image_and_close_fig(fig: matplotlib.figure, **kwargs):
    # Normally, dpi is set to 'figure', and the figure's dpi is set to 100.
    # So here we pick double of that to make things look good in a high
    # DPI display.
    options = {"bbox_inches": "tight", "dpi": 200, "format": "png"}

    # If some of the options are passed in from kwargs then replace
    # the values in options with the ones from kwargs
    options = {a: kwargs.get(a, b) for a, b in options.items()}
    # Merge options back into kwargs.
    kwargs.update(options)

    image = io.BytesIO()
    fig.savefig(image, **kwargs)
    plt.close(fig)

    return image


def plot_waveform(y, sample_rate):
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    librosa.display.waveplot(y, sr=sample_rate, x_axis='time', ax=ax)
    return get_image_and_close_fig(fig)


def plot_split_waveform(y, sample_rate):
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    y_harm, y_perc = librosa.effects.hpss(y)
    librosa.display.waveshow(y_harm, sr=sample_rate, alpha=0.5, ax=ax, label='Harmonic')
    librosa.display.waveshow(y_perc, sr=sample_rate, color='r', alpha=0.5, ax=ax, label='Percussive')
    ax.legend()
    return get_image_and_close_fig(fig)


def plot_stft(y, sample_rate):
    plt.style.use('dark_background')
    D = librosa.stft(y)  # STFT of y
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    fig, ax = plt.subplots()
    img = librosa.display.specshow(S_db, x_axis='time', y_axis='fft_note', ax=ax)
    fig.colorbar(img, ax=ax, format="%+2.f dB")
    return get_image_and_close_fig(fig)


def estimate_tempo(y, sample_rate, approximate_bpm):
    return librosa.beat.tempo(y, sr=sample_rate, start_bpm=approximate_bpm)[0]
