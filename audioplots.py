import numpy as np
from matplotlib import pyplot as plt
import librosa
from librosa import display

def audiosegment_to_librosa(segment):
    segment_file = segment.export(format='wav')
    y, sr = librosa.load(path=segment_file, sr=None)
    return y


def plot_waveform(y, sample_rate):
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    img = librosa.display.waveplot(y, sr=sample_rate, x_axis='time', ax=ax)
    return fig


def plot_split_waveform(y, sample_rate):
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    y_harm, y_perc = librosa.effects.hpss(y)
    librosa.display.waveshow(y_harm, sr=sample_rate, alpha=0.5, ax=ax, label='Harmonic')
    librosa.display.waveshow(y_perc, sr=sample_rate, color='r', alpha=0.5, ax=ax, label='Percussive')
    ax.legend()
    return fig


def plot_stft(y, sample_rate):
    plt.style.use('dark_background')
    D = librosa.stft(y)  # STFT of y
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    fig, ax = plt.subplots()
    img = librosa.display.specshow(S_db, x_axis='time', y_axis='fft_note', ax=ax)
    fig.colorbar(img, ax=ax, format="%+2.f dB")
    return fig


def estimate_tempo(y, sample_rate, approximate_bpm):
    return librosa.beat.tempo(y, sr=sample_rate, start_bpm=approximate_bpm)[0]