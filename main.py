import time
from typing import *

import pyaudio
from pydub import silence
from pydub import AudioSegment

from audio_io import *

ctx = {
    # names match pyaudio names
    "frames_per_buffer": 1024,   # Record in chunks of 1024 samples
    "format": pyaudio.paInt16,
    "channels": 2,
    "rate": 44100,  # Record at 44100 samples per second
}

aio = AudioIO(ctx)

while True:
    print('Recording')
    aio.start_recording()

    input("Press enter to hear what you just played ayy")
    sound: AudioSegment = aio.finish_recording()
    print('Finished recording')

    # print(sound.dBFS)
    # print(sound.max_dBFS)
    print(f'Recording duration: {len(sound) / 1000}s')

    start = time.time()
    fuckballs = silence.split_on_silence(sound,
                        min_silence_len=2000, # this dude will be modified by the user
                        silence_thresh=-80,  # FIXME: figure this out
                        keep_silence=100,
                        seek_step=1)
    end = time.time()
    print(f'Processing time to split on silence: {end - start}s')

    print(f'Found {len(fuckballs)} separate Clips')
    print(f'Last Clip duration: {len(fuckballs[-1]) / 1000}s')
    aio.play_audio(fuckballs[-1])

    print('Finished playback')

# Save the recorded data as a WAV file
# filename = "output.wav"
# wf = wave.open(filename, 'wb')
# wf.setnchannels(channels)
# wf.setsampwidth(p.get_sample_size(sample_format))
# wf.setframerate(fs)
# wf.writeframes(b''.join(frames))
# wf.close()

