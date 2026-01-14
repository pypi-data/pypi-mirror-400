from .utils import format_snippet

def mfcc_manual_vs_auto_code():
    code = '''
import os                 
import librosa            
import librosa.display    
import soundfile as sf    
import matplotlib.pyplot as plt  
import IPython.display as ipd    
import numpy as np               
from sklearn.metrics import mean_squared_error   
from scipy.fftpack import dct   

data_dir = "/kaggle/input/librispeech/dev-clean/"

#Free Lossless Audio Codec.

flac_files = []
for root, _, files in os.walk(data_dir):
    for file in files:
        if file.endswith(".flac"):
            flac_files.append(os.path.join(root, file))

print("Total .flac files found:", len(flac_files))
print("Example file path:", flac_files[0])

# Load one sample
sample_file = flac_files[0]
audio, sr = librosa.load(sample_file, sr=None)
print(f"Sample rate: {sr}, Duration: {len(audio)/sr:.2f} seconds")

# Listen to the audio
ipd.Audio(sample_file)

# Load .flac file

# Find first .flac file
flac_files = []
for root, _, files in os.walk(data_dir):
    for file in files:
        if file.endswith(".flac"):
            flac_files.append(os.path.join(root, file))
            
sample_file = flac_files[0]
print("Using file:", sample_file)

# Load audio
signal, sr = librosa.load(sample_file, sr=None)
print("Sample rate:", sr, "| Duration:", len(signal)/sr, "seconds")

# Implement MFCC from scratch

# ---------- Step 1: Pre-Emphasis ----------
def pre_emphasis(signal, coeff=0.97):
    return np.append(signal[0], signal[1:] - coeff * signal[:-1])

# ---------- Step 2: Framing ----------
def framing(signal, sr, frame_size=0.025, frame_stride=0.010):
    frame_length = int(frame_size * sr)
    frame_step = int(frame_stride * sr)
    num_frames = int(np.ceil(float(np.abs(len(signal) - frame_length)) / frame_step))
    
    pad_signal_length = num_frames * frame_step + frame_length
    z = np.zeros((pad_signal_length - len(signal)))
    pad_signal = np.append(signal, z)
    
    indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + \
              np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
    frames = pad_signal[indices.astype(np.int32, copy=False)]
    return frames

# ---------- Step 3: Windowing (Hamming) ----------
def hamming_window(N):
    return 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(N) / (N - 1))

def apply_window(frames):
    window = hamming_window(frames.shape[1])
    return frames * window

# ---------- Step 4: FFT and Power Spectrum ----------
def power_spectrum(frames, NFFT=512):
    mag_frames = np.absolute(np.fft.rfft(frames, NFFT))
    pow_frames = ((1.0 / NFFT) * (mag_frames ** 2))
    return pow_frames

# ---------- Step 5: Mel Filterbank ----------
def hz_to_mel(hz): return 2595 * np.log10(1 + hz / 700)
def mel_to_hz(mel): return 700 * (10**(mel / 2595) - 1)

def mel_filterbank(pow_frames, sr, NFFT=512, nfilt=26):
    low_mel = hz_to_mel(0)
    high_mel = hz_to_mel(sr / 2)
    mel_points = np.linspace(low_mel, high_mel, nfilt + 2)
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((NFFT + 1) * hz_points / sr).astype(int)
    
    fbank = np.zeros((nfilt, int(NFFT / 2 + 1)))
    for m in range(1, nfilt + 1):
        f_m_minus = bin_points[m - 1]
        f_m = bin_points[m]
        f_m_plus = bin_points[m + 1]
        
        for k in range(f_m_minus, f_m):
            fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
        for k in range(f_m, f_m_plus):
            fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)
    
    filter_banks = np.dot(pow_frames, fbank.T)
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
    return np.log(filter_banks)

# ---------- Step 6: DCT to Get MFCC ----------
def compute_mfcc(log_energies, num_ceps=13):
    mfcc = np.array([dct(f, type=2, norm='ortho')[:num_ceps] for f in log_energies])
    mfcc -= (np.mean(mfcc, axis=0) + 1e-8)
    return mfcc

# ---------- Step 7: Combine Everything ----------
def mfcc_from_scratch(signal, sr):
    emphasized = pre_emphasis(signal)
    frames = framing(emphasized, sr)
    windowed_frames = apply_window(frames)
    pow_frames = power_spectrum(windowed_frames)
    log_energies = mel_filterbank(pow_frames, sr)
    mfcc = compute_mfcc(log_energies)
    return mfcc

# Compute both versions (Scratch vs Librosa)

# Custom MFCC
mfcc_manual = mfcc_from_scratch(signal, sr)

# Librosa MFCC (reference)
mfcc_librosa = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)

print("Manual MFCC shape:", mfcc_manual.shape)
print("Librosa MFCC shape:", mfcc_librosa.T.shape)

# Compare numerically

# Align shapes
min_frames = min(mfcc_manual.shape[0], mfcc_librosa.shape[1])
mfcc_manual = mfcc_manual[:min_frames]
mfcc_librosa = mfcc_librosa[:, :min_frames].T

# Mean Squared Error (MSE)
mse = mean_squared_error(mfcc_manual.flatten(), mfcc_librosa.flatten())

# Signal-to-Noise Ratio (SNR)
signal_power = np.mean(mfcc_librosa ** 2)
noise_power = np.mean((mfcc_librosa - mfcc_manual) ** 2)
snr = 10 * np.log10(signal_power / noise_power)

print(f"MSE: {mse:.6f}")
print(f"SNR: {snr:.2f} dB")

# Visualize results
plt.figure(figsize=(14, 5))
plt.subplot(1, 2, 1)
librosa.display.specshow(mfcc_manual.T, sr=sr, x_axis='time')
plt.title("MFCC (From Scratch)")
plt.colorbar()

plt.subplot(1, 2, 2)
librosa.display.specshow(mfcc_librosa, sr=sr, x_axis='time')
plt.title("MFCC (Librosa)")
plt.colorbar()
plt.show()

# Evaluate on multiple files
mse_list, snr_list = [], []

for file in flac_files[:10]:  # limit to 10 files
    signal, sr = librosa.load(file, sr=None)
    mfcc_manual = mfcc_from_scratch(signal, sr)
    mfcc_librosa = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
    min_frames = min(mfcc_manual.shape[0], mfcc_librosa.shape[1])
    mfcc_manual = mfcc_manual[:min_frames]
    mfcc_librosa = mfcc_librosa[:, :min_frames].T
    mse = mean_squared_error(mfcc_manual.flatten(), mfcc_librosa.flatten())
    signal_power = np.mean(mfcc_librosa ** 2)
    noise_power = np.mean((mfcc_librosa - mfcc_manual) ** 2)
    snr = 10 * np.log10(signal_power / noise_power)
    mse_list.append(mse)
    snr_list.append(snr)

print(f"Average MSE across 10 files: {np.mean(mse_list):.6f}")
print(f"Average SNR across 10 files: {np.mean(snr_list):.2f} dB")

'''
    return format_snippet(code)

def analysis_formants_harmonics_code():
    code = '''
import numpy as np
from scipy.signal.windows import hamming
from scipy.linalg import lstsq
import matplotlib.pyplot as plt
import librosa

# y, sr = librosa.load('audio.wav', sr=None)
sr = 16000
t = np.linspace(0, 1.0, sr, endpoint=False)

f0 = 150
f1 = 500
f2 = 1500
f3 = 2500

y = 0.5 * np.sin(2 * np.pi * f0 * t)
y += 0.3 * np.sin(2 * np.pi * f1 * t) * np.exp(-10 * t)
y += 0.2 * np.sin(2 * np.pi * f2 * t) * np.exp(-10 * t)
y += 0.1 * np.sin(2 * np.pi * f3 * t) * np.exp(-10 * t)


def lpc_formants(sig, sr, order=10):

    if len(sig) < order + 1:
        print("Segment too short for the given LPC order.")
        return []

    sig = sig * hamming(len(sig))

    # Build the correlation matrix A
    A = np.zeros((len(sig)-order, order))
    for i in range(order):
        A[:, i] = sig[order-i-1:len(sig)-i-1]

    y_vec = sig[order:]

    # Solve for LPC coefficients 'a'
    a, _, _, _ = lstsq(A, y_vec)

    # Find roots of the prediction polynomial
    roots = np.roots(np.concatenate(([1], -a)))

    # Filter roots: keep only those in the upper half of the Z-plane
    roots = [r for r in roots if np.imag(r) >= 0]

    # Convert roots to angles/frequencies
    angles = np.arctan2(np.imag(roots), np.real(roots))

    # Convert to frequency (Hz)
    formants = sorted(angles * (sr / (2 * np.pi)))

    return formants[:3]


def estimate_harmonics(segment, sr, max_freq=4000):

    f0_contour = librosa.yin(segment, fmin=60, fmax=500, sr=sr)

    voiced_f0s = f0_contour[f0_contour > 0]

    if len(voiced_f0s) == 0:
        return 0, []

    estimated_f0 = np.median(voiced_f0s)
    harmonics = []
    n = 1
    while True:
        harmonic_freq = n * estimated_f0
        if harmonic_freq > max_freq:
            break
        if harmonic_freq > sr / 2: # nyquist thoerem
            break
        harmonics.append(harmonic_freq)
        n += 1

    return estimated_f0, harmonics


def plot_spectrum_analysis(segment, sr, formants, f0, harmonics):

    N = len(segment)

    # 1. Calculate Spectrum
    windowed_segment = segment * hamming(N)
    X = np.fft.fft(windowed_segment)

    # Get magnitude (first half only)
    X_mag = np.abs(X)[:N // 2]

    # Convert to decibels (dB)
    X_db = 20 * np.log10(X_mag / np.max(X_mag) + 1e-6)

    # Create the frequency axis
    freqs = np.fft.fftfreq(N, 1/sr)[:N // 2]

    plt.figure(figsize=(12, 6))
    plt.plot(freqs, X_db, label='Magnitude Spectrum (dB)', color='gray', alpha=0.7)

    if harmonics:
        harmonic_amplitudes = [X_db[np.argmin(np.abs(freqs - h))] for h in harmonics]
        plt.scatter(harmonics, harmonic_amplitudes, color='blue', marker='o', s=50,
                    label=f'Harmonics (F0 ≈ {f0:.1f} Hz)', zorder=5)

    if formants:
        for i, f in enumerate(formants):
            plt.axvline(x=f, color='red', linestyle='--', linewidth=2,
                        label=f'F{i+1}: {f:.1f} Hz' if i == 0 else None, zorder=3)


    plt.title('Frequency Spectrum with Formants (Filter) and Harmonics (Source)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.xlim(0, sr / 2)
    plt.ylim(np.max(X_db) - 60, np.max(X_db) + 5)
    plt.show()



segment = y[int(0.5*sr):int(0.7*sr)]

if len(segment) == 0:
    print("Segment empty")
else:
    order = int(sr / 1000) + 2
    formants = lpc_formants(segment, sr, order)
    estimated_f0, harmonics = estimate_harmonics(segment, sr)

    print(f"Estimated Pitch (Hz): {estimated_f0:.1f}")
    print(f"Estimated Formants (Hz): {[f'{f:.1f}' for f in formants]}")
    print(f"Harmonics count: {len(harmonics)}")

    plot_spectrum_analysis(segment, sr, formants, estimated_f0, harmonics)


'''
    return format_snippet(code)

def generate_consonants_code():
    code = '''
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio, display
import ipywidgets as widgets

sr = 16000  # Sampling rate
t = np.linspace(0, 0.5, int(0.5*sr))  # 0.5 seconds duration

def generate_consonant(consonant):
    """
    Generate simple synthetic consonant-like sounds
    using filtered noise and envelopes.
    """
    if consonant in ['S (s)', 'SH (sh)', 'F (f)']:
        # Fricatives: continuous noisy sounds
        y = np.random.randn(len(t)) * 0.3
        if consonant == 'S (s)':
            band = (4000, 8000)
        elif consonant == 'SH (sh)':
            band = (2000, 4000)
        elif consonant == 'F (f)':
            band = (1000, 4000)
        # Simple band-pass using FFT
        Y = np.fft.fft(y)
        freqs = np.fft.fftfreq(len(Y), 1/sr)
        mask = (np.abs(freqs) > band[0]) & (np.abs(freqs) < band[1])
        Y = Y * mask
        y = np.real(np.fft.ifft(Y))
    elif consonant in ['T (t)', 'P (p)']:
        # Stops: short bursts of energy
        y = np.zeros_like(t)
        burst_length = int(0.03 * sr)
        burst = np.random.randn(burst_length) * 0.8
        start = np.random.randint(1000, 3000)
        y[start:start+burst_length] = burst
    else:
        y = np.zeros_like(t)

    y /= np.max(np.abs(y) + 1e-6)
    return y

def show_consonant(consonant):
    y = generate_consonant(consonant)

    # Compute spectrum
    n = len(y)
    Y = np.abs(np.fft.fft(y))[:n//2]
    freq = np.fft.fftfreq(n, 1/sr)[:n//2]

    plt.figure(figsize=(10, 4))
    plt.plot(freq, Y)
    plt.title(f"Spectrum of Consonant: {consonant}")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.xlim(0, 8000)
    plt.grid(True)
    plt.show()

    display(Audio(y, rate=sr))

# Dropdown to choose consonant
consonant_dropdown = widgets.Dropdown(
    options=['S (s)', 'SH (sh)', 'F (f)', 'T (t)', 'P (p)'],
    description="Consonant:"
)

widgets.interactive(show_consonant, consonant=consonant_dropdown)

'''
    return format_snippet(code)

def lab2_code():
    code = '''
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
from scipy.signal import lfilter
from scipy.signal.windows import hamming
from numpy.linalg import lstsq
%matplotlib inline
import os
from google.colab import drive
from IPython.display import Audio

drive.mount(r'/content/drive')
os.chdir(r'/content/drive/MyDrive/English_Voice_&_Text_Dataset/voice')

def add_voice_line(audio_file):
  y, sr = librosa.load(audio_file, sr=None)

  Audio(y, rate=sr)

def plot_waveform(audio_file, title="Waveform"):
    y, sr = librosa.load(audio_file, sr=None)

    plt.figure(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr)
    plt.title(title)
    plt.xlabel("Time [s]")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def plot_linear_spectrogram(audio_file):
  y, sr = librosa.load(audio_file, sr=None)

  D = librosa.stft(y, n_fft=512)
  S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)

  plt.figure(figsize=(10, 6))
  librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
  plt.colorbar(label="Magnitude (dB)")
  plt.title("Linear-Frequency Spectrogram (STFT)")
  plt.ylim(0, 5000)
  plt.tight_layout()
  plt.show()

def plot_mel_spectrogram(audio_file):
  y, sr = librosa.load(audio_file, sr=None)

  # Mel-spectrogram
  S_mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=64, fmax=8000)
  S_mel_db = librosa.power_to_db(S_mel, ref=np.max)

  # Plot
  plt.figure(figsize=(10, 6))
  librosa.display.specshow(S_mel_db, x_axis='time', y_axis='mel', sr=sr, fmax=8000)
  plt.colorbar(label="dB")
  plt.title("Log-Mel Spectrogram")
  plt.tight_layout()
  plt.show()

def plot_pitch_histogram(audio_file):
  y, sr = librosa.load(audio_file, sr=None)

  pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
  pitch_values = pitches[magnitudes > np.median(magnitudes)]

  plt.figure(figsize=(8, 4))
  plt.hist(pitch_values, bins=50, color='teal', alpha=0.7)
  plt.title("Estimated Fundamental Frequencies (Pitch Histogram)")
  plt.xlabel("Frequency [Hz]")
  plt.ylabel("Count")
  plt.grid(True, alpha=0.3)
  plt.tight_layout()
  plt.show()

def plot_narrowband_spectrogram(audio_file):
  y, sr = librosa.load(audio_file, sr=None)

  D_narrow = librosa.stft(y, n_fft=512)
  S_narrow = librosa.amplitude_to_db(np.abs(D_narrow), ref=np.max)

  plt.figure(figsize=(10, 6))
  librosa.display.specshow(S_narrow, sr=sr, hop_length=512, x_axis='time', y_axis='hz')
  plt.colorbar(label="dB")
  plt.title("Narrowband Spectrogram (Harmonics Visible)")
  plt.ylim(0, 3000)
  plt.tight_layout()
  plt.show()

def plot_wideband_spectrogram(audio_file):
  y, sr = librosa.load(audio_file, sr=None)

  D_wide = librosa.stft(y, n_fft=512, hop_length=128)
  S_wide = librosa.amplitude_to_db(np.abs(D_wide), ref=np.max)

  plt.figure(figsize=(10, 6))
  librosa.display.specshow(S_wide, sr=sr, hop_length=128, x_axis='time', y_axis='hz')
  plt.colorbar(label="dB")
  plt.title("Wideband Spectrogram (Formant Transitions)")
  plt.ylim(0, 4000)
  plt.tight_layout()
  plt.show()

for voice_file in os.listdir():

  print(f"Processing file: {voice_file}")
  add_voice_line(voice_file)
  plot_waveform(voice_file)
  plot_linear_spectrogram(voice_file)
  plot_mel_spectrogram(voice_file)
  plot_pitch_histogram(voice_file)

  print("\n Narrowband Spectrogram:")
  plot_narrowband_spectrogram(voice_file)

  print("\n Wideband Spectrogram:")
  plot_wideband_spectrogram(voice_file)

'''
    return format_snippet(code)

def quiz_code():
    code = '''
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import os
from google.colab import drive
from IPython.display import Audio

# Mount Google Drive
drive.mount('/content/drive')

# Change to the directory containing the audio files
os.chdir('/content/drive/MyDrive/English_Voice_&_Text_Dataset/voice')

# --- Q1: Waveform Segmentation & Analysis ---

# 1. Load the waveform
AUDIO_FILE = 'voice_1.wav'
y, sr = librosa.load(AUDIO_FILE, sr=None)

# Play the audio (optional)
print(f"Processing file: {AUDIO_FILE}")
Audio(y, rate=sr)

# 2. Plot the first 50 ms with amplitude normalization
fifty_ms_samples = int(0.05 * sr)
y_50ms = y[:fifty_ms_samples]

# Normalize amplitude to [-1, 1] if not already
if np.max(np.abs(y_50ms)) > 0:
    y_50ms_normalized = y_50ms / np.max(np.abs(y_50ms))
else:
    y_50ms_normalized = y_50ms # Avoid division by zero if audio is silent

t_50ms = np.linspace(0, 0.05, len(y_50ms_normalized), endpoint=False)

plt.figure(figsize=(12, 4))
plt.plot(t_50ms, y_50ms_normalized)
plt.title(f"First 50ms of '{AUDIO_FILE}' (Normalized Amplitude)")
plt.xlabel("Time [s]")
plt.ylabel("Normalized Amplitude")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 3. Segment the waveform into two parts (example: first 0.5s as word 1, rest as word 2)
segment_point_s = 0.5
segment_point_samples = int(segment_point_s * sr)

# Ensure segment_point_samples does not exceed audio length
if segment_point_samples >= len(y):
    print("Warning: Audio is shorter than 0.5 seconds. Adjusting segmentation.")
    segment_point_samples = len(y) // 2 # Segment into two equal halves if too short

y_word1 = y[:segment_point_samples]
y_word2 = y[segment_point_samples:]

t_word1 = np.linspace(0, len(y_word1)/sr, len(y_word1), endpoint=False)
t_word2 = np.linspace(len(y_word1)/sr, len(y)/sr, len(y_word2), endpoint=False)

# 4. Plot both segments and compute their energy
plt.figure(figsize=(12, 6))

plt.subplot(2, 1, 1)
plt.plot(t_word1, y_word1)
plt.title(f"Segment 1 (0-{segment_point_s}s) of '{AUDIO_FILE}'")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True, alpha=0.3)

plt.subplot(2, 1, 2)
plt.plot(t_word2, y_word2)
plt.title(f"Segment 2 ({segment_point_s}s-End) of '{AUDIO_FILE}'")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

energy_word1 = np.sum(y_word1**2)
energy_word2 = np.sum(y_word2**2)

print(f"Energy of Segment 1 (0-{segment_point_s}s): {energy_word1:.2f}")
print(f"Energy of Segment 2 ({segment_point_s}s-End): {energy_word2:.2f}")

# 5. Voicing dominance analysis
print("\n--- Voicing Dominance Analysis ---")
if energy_word1 > energy_word2:
    print(f"Segment 1 (first {segment_point_s}s) has higher energy ({energy_word1:.2f}) than Segment 2 ({energy_word2:.2f}), suggesting it might be more voiced-dominant or contain louder speech.")
elif energy_word2 > energy_word1:
    print(f"Segment 2 (after {segment_point_s}s) has higher energy ({energy_word2:.2f}) than Segment 1 ({energy_word1:.2f}), suggesting it might be more voiced-dominant or contain louder speech.")
else:
    print("Both segments have similar energy, implying comparable voicing characteristics or loudness.")


# --- Q2: Spectrogram Exploration ---

plt.figure(figsize=(15, 8))

# 1. Compute and plot STFT Spectrogram
plt.subplot(1, 2, 1)
D = librosa.stft(y)
S_db_stft = librosa.amplitude_to_db(np.abs(D), ref=np.max)
librosa.display.specshow(S_db_stft, sr=sr, x_axis='time', y_axis='hz')
plt.colorbar(format='%+2.0f dB')
plt.title('STFT Spectrogram (Log-scaled)')
plt.xlabel("Time [s]")
plt.ylabel("Frequency [Hz]")
plt.ylim(0, sr/2) # Show full frequency range

# 2. Compute and plot Mel-Spectrogram
plt.subplot(1, 2, 2)
S_mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
S_db_mel = librosa.power_to_db(S_mel, ref=np.max)
librosa.display.specshow(S_db_mel, sr=sr, x_axis='time', y_axis='mel')
plt.colorbar(format='%+2.0f dB')
plt.title('Mel-Spectrogram (Log-scaled)')
plt.xlabel("Time [s]")
plt.ylabel("Mel-frequency")
plt.tight_layout()
plt.show()

'''
    return format_snippet(code)

def oel1_code():
    code = '''
#GENERATE AND SAVE DATASET
import numpy as np
import matplotlib.pyplot as plt
import librosa
from IPython.display import Audio, display
from sklearn.metrics import mean_squared_error
from scipy.fftpack import dct

sr = 16000
t = np.linspace(0, 1, sr)

#ONLY GENERATE
def gen_audio(f0, f1, f2):
  y = np.sin(2*np.pi*f0*t)
  y = y + (0.5 * np.sin(2*np.pi*f1*t))
  y = y + (0.3 * np.sin(2*np.pi*f2*t))
  y = y / (np.max(np.abs(y)))
  return y

m1 = gen_audio(200, 730, 1090) #A
m2 = gen_audio(200, 530, 1840) #E
m3 = gen_audio(200, 270, 2290) #I
f1 = gen_audio(300, 790, 1160) #A
f2 = gen_audio(300, 600, 2070) #E
f3 = gen_audio(300, 330, 2680) #I

#GENERATE PLUS SAVE
male_aa = gen_audio(250, 700, 1200)
male_ee = gen_audio(250, 600, 1900)
male_oo = gen_audio(250, 300, 2300)

female_aa = gen_audio(350, 750, 1300)
female_ee = gen_audio(350, 650, 2000)
female_oo = gen_audio(350, 350, 2400)

speakers_dataset = {
    "male": {
        "aa": male_aa,
        "ee": male_ee,
        "oo": male_oo
    },
    "female": {
        "aa": female_aa,
        "ee": female_ee,
        "oo": female_oo
    }
}

print("Generated dataset structure:")
for speaker, phonemes in speakers_dataset.items():
    print(f"Speaker: {speaker}")
    for phoneme, audio in phonemes.items():
        print(f"  Phoneme '{phoneme}': Audio array of shape {audio.shape}")

import os
import soundfile as sf
import librosa

# Define the base directory for audio data
base_audio_dir = 'audio_data'

# Create the base directory if it doesn't exist
os.makedirs(base_audio_dir, exist_ok=True)

print(f"Saving audio files to: {base_audio_dir}")

# Iterate through speakers_dataset to save audio files
for speaker_name, phonemes in speakers_dataset.items():
    speaker_dir = os.path.join(base_audio_dir, speaker_name)
    os.makedirs(speaker_dir, exist_ok=True)
    for phoneme_name, audio_data in phonemes.items():
        file_path = os.path.join(speaker_dir, f"{phoneme_name}.wav")
        sf.write(file_path, audio_data, sr)
        print(f"  Saved {file_path}")

print("\nLoading audio files back into a new dictionary...")

# Initialize an empty dictionary to load audio files into
loaded_speakers_dataset = {}

# Iterate through the created directory structure to load WAV files
for speaker_name in os.listdir(base_audio_dir):
    speaker_path = os.path.join(base_audio_dir, speaker_name)
    if os.path.isdir(speaker_path):
        loaded_speakers_dataset[speaker_name] = {}
        for phoneme_file in os.listdir(speaker_path):
            if phoneme_file.endswith('.wav'):
                phoneme_name = os.path.splitext(phoneme_file)[0] # Remove .wav extension
                file_path = os.path.join(speaker_path, phoneme_file)
                
                # Load the audio file using librosa.load
                # librosa.load returns (audio_array, sampling_rate)
                audio_array, current_sr = librosa.load(file_path, sr=sr) # Ensure consistent sr
                
                loaded_speakers_dataset[speaker_name][phoneme_name] = audio_array
                print(f"  Loaded {file_path} (shape: {audio_array.shape}, sr: {current_sr})")

print("\nStructure of loaded_speakers_dataset:")
for speaker, phonemes in loaded_speakers_dataset.items():
    print(f"Speaker: {speaker}")
    for phoneme, audio in phonemes.items():
        print(f"  Phoneme '{phoneme}': Audio array of shape {audio.shape}")

'''
    return format_snippet(code)

def mfcc_from_scratch_code():
    code = '''
# ---------- Step 1: Pre-Emphasis ----------
def pre_emphasis(signal, coeff=0.97):
    return np.append(signal[0], signal[1:] - coeff * signal[:-1])

# ---------- Step 2: Framing ----------
def framing(signal, sr, frame_size=0.025, frame_stride=0.010):
    frame_length = int(frame_size * sr)
    frame_step = int(frame_stride * sr)
    num_frames = int(np.ceil(float(np.abs(len(signal) - frame_length)) / frame_step))

    pad_signal_length = num_frames * frame_step + frame_length
    z = np.zeros((pad_signal_length - len(signal)))
    pad_signal = np.append(signal, z)

    indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + \
              np.tile(np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
    frames = pad_signal[indices.astype(np.int32, copy=False)]
    return frames

# ---------- Step 3: Windowing (Hamming) ----------
def hamming_window(N):
    return 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(N) / (N - 1))

def apply_window(frames):
    window = hamming_window(frames.shape[1])
    return frames * window

# ---------- Step 4: FFT and Power Spectrum ----------
def power_spectrum(frames, NFFT=512):
    mag_frames = np.absolute(np.fft.rfft(frames, NFFT))
    pow_frames = ((1.0 / NFFT) * (mag_frames ** 2))
    return pow_frames

# ---------- Step 5: Mel Filterbank ----------
def hz_to_mel(hz): return 2595 * np.log10(1 + hz / 700)
def mel_to_hz(mel): return 700 * (10**(mel / 2595) - 1)

def mel_filterbank(pow_frames, sr, NFFT=512, nfilt=26):
    low_mel = hz_to_mel(0)
    high_mel = hz_to_mel(sr / 2)
    mel_points = np.linspace(low_mel, high_mel, nfilt + 2)
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((NFFT + 1) * hz_points / sr).astype(int)

    fbank = np.zeros((nfilt, int(NFFT / 2 + 1)))
    for m in range(1, nfilt + 1):
        f_m_minus = bin_points[m - 1]
        f_m = bin_points[m]
        f_m_plus = bin_points[m + 1]

        for k in range(f_m_minus, f_m):
            fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
        for k in range(f_m, f_m_plus):
            fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

    filter_banks = np.dot(pow_frames, fbank.T)
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
    return np.log(filter_banks)

# ---------- Step 6: DCT to Get MFCC ----------
def compute_mfcc(log_energies, num_ceps=13):
    mfcc = np.array([dct(f, type=2, norm='ortho')[:num_ceps] for f in log_energies])
    mfcc -= (np.mean(mfcc, axis=0) + 1e-8)
    return mfcc

# ---------- Step 7: Combine Everything ----------
def mfcc_from_scratch(signal, sr):
    emphasized = pre_emphasis(signal)
    frames = framing(emphasized, sr)
    windowed_frames = apply_window(frames)
    pow_frames = power_spectrum(windowed_frames)
    log_energies = mel_filterbank(pow_frames, sr)
    mfcc = compute_mfcc(log_energies)
    return mfcc

def mffcs_all(y, sr, title):
  mfcc = mfcc_from_scratch(y, sr)
  print("M1 MFCC shape:", mfcc.shape)

  plt.figure(figsize=(14, 5))
  plt.subplot(1, 2, 1)
  librosa.display.specshow(mfcc.T, sr=sr, x_axis='time')
  plt.title(title)
  plt.colorbar()

'''
    return format_snippet(code)

def mfcc_feature_extraction_code():
    code = '''
# Libraries
import numpy as np
import matplotlib.pyplot as plt
import librosa
import wave
from scipy.fftpack import dct

# Step:1 Load and visualize waveform
filename = "/kaggle/input/voices/voices/vowels.ogg"

# Load using librosa (automatically converts to mono & 16 kHz)
signal, sr = librosa.load(filename, sr=16000)

# Normalize
signal = signal / np.max(np.abs(signal))

# Plot waveform
time = np.linspace(0, len(signal) / sr, len(signal)) # total number of samples
plt.figure(figsize=(10, 3))
plt.plot(time, signal)
plt.title("Original Waveform")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.show()

print("Sampling Rate:", sr)
print("\n=== Step 1: Original Signal Samples ===")
print(signal[:20])

# STEP 2: PRE-EMPHASIS
def pre_emphasis(sig, coeff=0.97):
    emphasized = np.append(sig[0], sig[1:] - coeff * sig[:-1])
    return emphasized

# Apply pre-emphasis
emphasized = pre_emphasis(signal)

# Numerical comparison for first few samples
print("=== Step 2: Pre-Emphasis ===")
for i in range(11,20):
    print(f"Sample {i}: Original = {signal[i]:.8f}, Emphasized = {emphasized[i]:.8f}")

# Plot both signals on the same graph (like your image)
plt.figure(figsize=(10, 4))
plt.plot(signal[:200], color='blue', label='Original')
plt.plot(emphasized[:200], color='orange', label='Pre-emphasized')
plt.title("Pre-emphasis Effect (first 200 samples)")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.show()

# STEP 3: FRAMING
frame_size = int(0.025 * sr)   # 25 ms
frame_shift = int(0.010 * sr)  # 10 ms

frames = []
for start in range(0, len(emphasized) - frame_size, frame_shift):
    frames.append(emphasized[start:start + frame_size])
frames = np.array(frames)

print("\n=== Step 3: Total Frames ===", len(frames))
print("Frame length:", frame_size, "samples")
print("Frame Shift:",frame_shift)


# Plot signal with frame windows shown
plt.figure(figsize=(10, 4))
t = np.linspace(0, 0.5,len(signal))
plt.plot(t, signal, color='blue')
plt.title("Framing Visualization")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")

# Draw frame windows on waveform
colors = ['red', 'green', 'orange']
for i, start in enumerate(range(0, len(signal) - frame_size, frame_shift)[:3]):  # Show 5 frames
    start_time = start / sr
    end_time = (start + frame_size) / sr
    plt.axvspan(start_time, end_time, color=colors[i % len(colors)], alpha=0.2, label=f"Frame {i+1}")

plt.legend()
plt.grid(True)
plt.show()

# Step 4: HAMMING WINDOW
# Define Hamming window function
def hamming_window(N):
    return 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(N) / (N - 1))


window = hamming_window(frame_size)
windowed_frames = frames * window

# Select any frame to visualize
frame_index = 11
original_frame = frames[frame_index]
windowed_frame = windowed_frames[frame_index]

# Plot first 200 samples of original vs. windowed frame
plt.figure(figsize=(10, 4))
plt.plot(original_frame[:200], color='blue', label='Original Frame')
plt.plot(windowed_frame[:200], color='orange', label='Windowed Frame')
plt.title("Hamming Window Effect on First 200 Samples")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.show()

# Optional: Plot the Hamming window itself for first 200 samples
plt.figure(figsize=(8, 3))
plt.plot(window[:800], color='green')
plt.title("Hamming Window Shape (First 200 Samples)")
plt.xlabel("Sample Index")
plt.ylabel("Window Value")
plt.grid(True)
plt.show()

# Step 5: FFT & POWER SPECTRUM
NFFT = 512
def power_spectrum(frame, NFFT):
    mag = np.abs(np.fft.rfft(frame, NFFT))   # positive frequency
    power = (1.0 / NFFT) * (mag ** 2)
    return power

power_frames = np.array([power_spectrum(f, NFFT) for f in windowed_frames])

plt.figure(figsize=(10, 4))
plt.plot(10 * np.log10(power_frames[0]))
plt.title("Power Spectrum (First Frame, dB Scale)")
plt.xlabel("Frequency Bins")
plt.ylabel("Power (dB)")
plt.show()

# Step 6: MEL FILTERBANK
def hz_to_mel(hz): return 2595 * np.log10(1 + hz / 700)
def mel_to_hz(mel): return 700 * (10**(mel / 2595) - 1)

n_filters = 26
low_mel = hz_to_mel(0)
high_mel = hz_to_mel(sr / 2)
mel_points = np.linspace(low_mel, high_mel, n_filters + 2)
hz_points = mel_to_hz(mel_points)
bin_points = np.floor((NFFT + 1) * hz_points / sr).astype(int)

fbank = np.zeros((n_filters, int(NFFT / 2 + 1)))
for m in range(1, n_filters + 1):
    f_m_minus = bin_points[m - 1]
    f_m = bin_points[m]
    f_m_plus = bin_points[m + 1]
    for k in range(f_m_minus, f_m):
        fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
    for k in range(f_m, f_m_plus):
        fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

plt.figure(figsize=(10, 4))
for i in range(n_filters):
    plt.plot(fbank[i])
plt.title("Mel Filterbank (Triangular Filters)")
plt.xlabel("Frequency Bins")
plt.ylabel("Amplitude")
plt.show()

# Step 7: FILTER ENERGIES (LOG SCALE)
filter_banks = np.dot(power_frames, fbank.T)
filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
log_energies = np.log(filter_banks)

plt.imshow(log_energies.T, aspect='auto', origin='lower')
plt.title("Mel Filterbank Energies (Log Scale)")
plt.xlabel("Frame Index")
plt.ylabel("Filter Index")
plt.show()

# Step:8 MFCCs(Mel-Frequency Cepstral Coefficients)
num_ceps = 13
mfccs = np.array([dct(f, type=2, norm='ortho')[:num_ceps] for f in log_energies])
mfccs -= (np.mean(mfccs, axis=0) + 1e-8)

plt.imshow(mfccs.T, aspect='auto', origin='lower')
plt.title("MFCCs (13 Coefficients per Frame)")
plt.xlabel("Frame Index")
plt.ylabel("Coefficient Index")
plt.colorbar(label="Coefficient Value")
plt.show()

print("\n=== Step 8: MFCCs (first frame, all coefficients) ===")
print(mfccs[0])


'''
    return format_snippet(code)

def mfcc_file_features_code():
    code = '''
# Libraries
import os
import numpy as np
import pandas as pd
import librosa
from scipy.fftpack import dct

dataset_path = '/content/audio_dataset'
sr = 16000

# MFCC coefficients
num_ceps = 13  

# --- FUNCTIONS  ---

def pre_emphasis(sig, coeff=0.97):
    return np.append(sig[0], sig[1:] - coeff * sig[:-1])

def hamming_window(N):
    return 0.54 - 0.46 * np.cos(2 * np.pi * np.arange(N) / (N - 1))

def power_spectrum(frame, NFFT=512):
    mag = np.abs(np.fft.rfft(frame, NFFT))
    power = (1.0 / NFFT) * (mag ** 2)
    return power

def hz_to_mel(hz):
    return 2595 * np.log10(1 + hz / 700)

def mel_to_hz(mel):
    return 700 * (10 ** (mel / 2595) - 1)

def mel_filterbank(sr=16000, NFFT=512, n_filters=26):
    low_mel = hz_to_mel(0)
    high_mel = hz_to_mel(sr / 2)
    mel_points = np.linspace(low_mel, high_mel, n_filters + 2)
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((NFFT + 1) * hz_points / sr).astype(int)
    
    fbank = np.zeros((n_filters, int(NFFT / 2 + 1)))
    for m in range(1, n_filters + 1):
        f_m_minus, f_m, f_m_plus = bin_points[m - 1], bin_points[m], bin_points[m + 1]
        for k in range(f_m_minus, f_m):
            fbank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
        for k in range(f_m, f_m_plus):
            fbank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)
    return fbank
    
# --- MAIN MFCC EXTRACTION FUNCTION ---

def extract_mfcc_from_file(filepath, sr=16000, num_ceps=13):
    # 1. Load and normalize audio
    signal, sr = librosa.load(filepath, sr=sr)
    signal = signal / np.max(np.abs(signal))
    
    # 2. Pre-emphasis
    emphasized = pre_emphasis(signal)
    
    # 3. Framing
    frame_size = int(0.025 * sr)
    frame_shift = int(0.010 * sr)
    frames = []
    for start in range(0, len(emphasized) - frame_size, frame_shift):
        frames.append(emphasized[start:start + frame_size])
    frames = np.array(frames)
    
    # 4. Apply Hamming Window
    window = hamming_window(frame_size)
    windowed_frames = frames * window
    
    # 5. Power Spectrum
    NFFT = 512
    power_frames = np.array([power_spectrum(f, NFFT) for f in win-dowed_frames])
    
    # 6. Mel Filterbank
    fbank = mel_filterbank(sr, NFFT)
    filter_banks = np.dot(power_frames, fbank.T)
    filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, fil-ter_banks)
    log_energies = np.log(filter_banks)
    
    # 7. MFCCs
    mfccs = np.array([dct(f, type=2, norm='ortho')[:num_ceps] for f in log_energies])
    mfccs -= (np.mean(mfccs, axis=0) + 1e-8)
    
    # Return mean of MFCCs across frames (to get one feature vector per file)
    return np.mean(mfccs, axis=0)

# --- PROCESS ALL FILES ---

all_features = []
file_names = []

for file in os.listdir(dataset_path):
    if file.endswith(".wav"):
        filepath = os.path.join(dataset_path, file)
        print(f"Processing: {file}")
        mfcc_vector = extract_mfcc_from_file(filepath, sr, num_ceps)
        all_features.append(mfcc_vector)
        file_names.append(file)

# --- SAVE FEATURES TO CSV ---

df = pd.DataFrame(all_features, columns=[f"MFCC_{i+1}" for i in range(num_ceps)])
df.insert(0, "Filename", file_names)
output_csv = "/content/mfcc_features.csv"
df.to_csv(output_csv, index=False)

print("\n MFCC feature extraction complete!")
print(f"Saved to: {output_csv}")

# Preview first few rows
df.head()


'''
    return format_snippet(code)