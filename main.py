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

print('Recording')

aio.start_recording()
time.sleep(5)
sound: AudioSegment = aio.finish_recording()

print('Finished recording')

print(sound.dBFS)
print(sound.max_dBFS)
print(f'Clip Duration: {len(sound)}')

start = time.time()
fuckballs = silence.split_on_silence(sound,
                    min_silence_len=1000, # this dude will be modified buy the user
                    silence_thresh=-80,  # FIXME: figure this out
                    keep_silence=100,
                    seek_step=1)
end = time.time()
print("Time elapsed:", end - start)

print(f'Found {len(fuckballs)} separate clips')
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

