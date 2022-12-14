# -*- coding: utf-8 -*-
"""denoising.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1UvH2PoPuYsPhovqwEUAwU6xjo6c6tqtR

# connecting g drive
"""

# from google.colab import drive
# drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# %cd /content/drive/My Drive/Colab Notebooks/
# %cd /content/drive/MyDrive/Colab Notebooks/FYP

"""# import modules"""


"""# loading previously trained model"""

# from pydub import AudioSegment

import noisereduce as nr
import numpy as np
import librosa
import librosa.display
import IPython.display as ipd
import matplotlib.pyplot as plt
from keras.models import load_model
import soundfile as sf
from os import path
import shutil
import subprocess
model = load_model(
    r'model/denoiser_batchsize_5_epoch_100_sample_2000_org_n_n.hdf5', compile=True)

"""# testing on real world audio 

"""

# function of moving point average used for minimizing distortion in denoised audio.

# files


# def mp3_to_wav(src_path, dest_path):

#     # convert wav to mp3
#     subprocess.call(['ffmpeg', '-i', src_path,
#                      dest_path])


# os.system("python mp3__to_wav.py 1")


def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


# mp3_to_wav("uploads/recording.mp3", "uploads/test.wav")
# audio , sr =  librosa.load(r'real_world_data/noise speech.wav' , res_type='kaiser_fast')
audio, sr = librosa.load(
    r'../client/src/denoised-audio/recording.wav', res_type='kaiser_fast')


# audio, sr =  librosa.load(r'real_world_data/babar.wav', res_type='kaiser_fast')
# audio, sr =  librosa.load(r'real_world_data/sarfaraz_eng.wav', res_type='kaiser_fast')

print(audio)
print(len(audio))
ipd.Audio(data=audio, rate=22050)

real_audio_spec = np.abs(librosa.stft(audio))
fig, ax = plt.subplots()

img = librosa.display.specshow(librosa.amplitude_to_db(
    real_audio_spec, ref=np.max), y_axis='log', x_axis='time', ax=ax)

ax.set_title('Power spectrogram input real audio ')

fig.colorbar(img, ax=ax, format="%+2.0f dB")

ipd.Audio(data=audio, rate=22050)

start = 0
end = 65536

print(len(audio))
print(len(audio)/22050)

split_range = int(len(audio) / 65536)
print(split_range)
# zeros = len(audio) % 65536

# zeros = int(len(audio) - 65536 * (len(audio) / 65536))
# zero_arr = [0] * zeros
# audio = np.concatenate((audio, zero_arr), axis=0)

predicted_noise = []
input_audio = []
# TODO  : REMOVE CLIPPING OF AUDIO AT THE END.
for i in range(split_range + 1):

    audio_frame = audio[start:end]
    if (len(audio_frame) % 65536 != 0):
        needed_zeros = 0
        needed_zeros = 65536 - len(audio_frame)
        zero_arr = [0] * needed_zeros
        audio_frame = np.concatenate((audio_frame, zero_arr), axis=0)

    input_audio.append(audio_frame)
    audio_reshape = np.reshape(audio_frame, (1, 256, 256, 1))

    prediction = model.predict(audio_reshape)

    prediction = prediction.flatten()

    predicted_noise.append([prediction])

    start = start + 65536
    end = end + 65536


predicted_noise = np.asarray(predicted_noise).flatten()
input_audio = np.asarray(input_audio).flatten()
real_pred_noise_spec = np.abs(librosa.stft(predicted_noise))

"""## input audio to model"""

ipd.Audio(data=input_audio, rate=22050)

# sf.write('denoised/input_audio.wav',
#          input_audio.astype(np.float32), 22050, 'PCM_16')

fig, ax = plt.subplots()

img = librosa.display.specshow(librosa.amplitude_to_db(
    real_pred_noise_spec, ref=np.max), y_axis='log', x_axis='time', ax=ax)

ax.set_title('Power spectrogram pred noise of real audio ')

fig.colorbar(img, ax=ax, format="%+2.0f dB")
ipd.Audio(data=predicted_noise, rate=22050)

# sf.write('denoised/predicted_noise.wav', predicted_noise.astype(
#     np.float32), 22050, 'PCM_16')

ipd.Audio(data=moving_average(predicted_noise, 8), rate=22050)

denoised_final_audio = input_audio - predicted_noise
real_denoised_audio_spec = np.abs(librosa.stft(denoised_final_audio))

fig, ax = plt.subplots()

img = librosa.display.specshow(librosa.amplitude_to_db(
    real_denoised_audio_spec, ref=np.max), y_axis='log', x_axis='time', ax=ax)

ax.set_title('Power spectrogram final denoised real audio ')

fig.colorbar(img, ax=ax, format="%+2.0f dB")

ipd.Audio(data=denoised_final_audio, rate=22050)

# sf.write('denoised/denoised_final_audio_by_model.wav',
#          denoised_final_audio.astype(np.float32), 22050, 'PCM_16')

"""## moving point average of the real world denoised signal"""

real_world_mov_avg = moving_average(denoised_final_audio, 4)
print(real_world_mov_avg)
print(len(real_world_mov_avg))
ipd.Audio(data=real_world_mov_avg,  rate=22050)

"""## noise reduce library"""

# !pip install noisereduce

"""### nr on real world audio"""

# if you cant import it. than you need to install it using 'pip install noisereduce'

"""#### using noise reduce directly on the real world audio to see how it works on it. """

reduced_noise_direct = nr.reduce_noise(
    y=audio.flatten(), sr=22050, stationary=False)
ipd.Audio(data=reduced_noise_direct, rate=22050)

# sf.write('denoised/denoised_input_audio_direct_by_noisereduce_no_model.wav',
#          reduced_noise_direct.astype(np.float32), 22050, 'PCM_16')

"""#### using noise reduce on model denoised final output. to make it more clean."""

# perform noise reduction
reduced_noise = nr.reduce_noise(y=real_world_mov_avg.flatten(
), sr=22050, y_noise=predicted_noise, stationary=False)

# wavfile.write("mywav_reduced_noise.wav", rate, reduced_noise)
ipd.Audio(data=reduced_noise, rate=22050)

sf.write(r'../client/src/denoised-audio/denoised.wav',
         reduced_noise.astype(np.float32), 22050, 'PCM_16')

#  spectrogram generation for noisy input and denoised output
print("making spectrograms")
noisy_path = r'../client/src/denoised-audio/recording.wav'
denoised_path = r'../client/src/denoised-audio/denoised.wav'

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

fig.savefig(r'../client/src/recorded-audio-spectograms/spec_noisy.png')

# for denoised spectrogram.
fig, ax = plt.subplots()
S_dB_denoised = librosa.power_to_db(S_denoised, ref=np.max)
img_denoised = librosa.display.specshow(
    S_dB_denoised, x_axis='time', y_axis='mel', sr=sr_denoised, fmax=8000, ax=ax)
fig.colorbar(img_denoised, ax=ax, format='%+2.0f dB')
ax.set(title='Mel-frequency spectrogram denoised')

fig.savefig(
    r'../client/src/recorded-audio-spectograms/spec_denoised.png')
# spectrogram generation and saving ka kaam idher katam.

print("python code executed")
