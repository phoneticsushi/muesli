import numpy as np
from matplotlib import pyplot as plt
import librosa
from librosa import display

def plot_waveform(y, sample_rate):
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    img = librosa.display.waveplot(y, sr=sample_rate, x_axis='time', ax=ax)
    return fig

def plot_stft(y, sample_rate):
    plt.style.use('dark_background')
    D = librosa.stft(y)  # STFT of y
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    fig, ax = plt.subplots()
    img = librosa.display.specshow(S_db, x_axis='time', y_axis='linear', ax=ax)
    fig.colorbar(img, ax=ax, format="%+2.f dB")
    return fig
