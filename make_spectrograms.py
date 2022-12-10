import matplotlib.pyplot as plt
import librosa.display

import numpy as np
import pandas as pd
import librosa

import matplotlib.pyplot as plt


# filename = librosa.util.example_audio_file()
noisy_path = r'E:/toil/FYP/server/tmp/video.wav'
denoised_path = r'E:/toil/FYP/server/tmp/denoised_boosted.wav'


noisy, sr_noisy = librosa.load(noisy_path)
denoised, sr_denoised = librosa.load(denoised_path)

S_noisy = librosa.feature.melspectrogram(
    y=noisy, sr=sr_noisy, n_mels=128, fmax=8000)

S_denoised = librosa.feature.melspectrogram(
    y=denoised, sr=sr_noisy, n_mels=128, fmax=8000)


# for noisy input audio.
fig, ax = plt.subplots()
S_dB_noisy = librosa.power_to_db(S_noisy, ref=np.max)
img_noisy = librosa.display.specshow(
    S_dB_noisy, x_axis='time', y_axis='mel', sr=sr_noisy, fmax=8000, ax=ax)
fig.colorbar(img_noisy, ax=ax, format='%+2.0f dB')
ax.set(title='Mel-frequency spectrogram noisy')

fig.savefig('spectrogram_to_show_on_web/spec_noisy.png')

# for denoised spectrogram.
fig, ax = plt.subplots()
S_dB_denoised = librosa.power_to_db(S_denoised, ref=np.max)
img_denoised = librosa.display.specshow(
    S_dB_denoised, x_axis='time', y_axis='mel', sr=sr_denoised, fmax=8000, ax=ax)
fig.colorbar(img_denoised, ax=ax, format='%+2.0f dB')
ax.set(title='Mel-frequency spectrogram denoised')

fig.savefig('spectrogram_to_show_on_web/spec_denoised.png')
