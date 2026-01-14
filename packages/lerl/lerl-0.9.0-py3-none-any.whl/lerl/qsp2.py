from .utils import format_snippet

def sp_lstm_code():
    code = '''
#LSTM
import librosa        
import librosa.display 
import matplotlib.pyplot as plt 
import numpy as np
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential 
from tensorflow.keras.layers import LSTM, Dense, Dropout

audio_path = '/kaggle/input/speech-sounds/Sounds-speech/No-3.wav' 
y, sr = librosa.load(audio_path, sr=None)

print("Sampling Rate:", sr)
print("Duration (seconds):", len(y)/sr)


plt.figure(figsize=(10,4))
librosa.display.waveshow(y, sr=sr)
plt.title("Speech Waveform")
plt.xlabel("Time")
plt.ylabel("Amplitude")
plt.show()


mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13) 
print("MFCC shape:", mfcc.shape)

mfcc_seq = mfcc.T
mfcc_seq = (mfcc_seq - np.mean(mfcc_seq)) / np.std(mfcc_seq)



DATASET_PATH = '/kaggle/input/speech-sounds/Sounds-speech'
X, y_labels = [], []


for file in os.listdir(DATASET_PATH): 
    if file.endswith('.wav'):
        label = 1 if file.lower().startswith('yes') else 0
        signal, sr = librosa.load(os.path.join(DATASET_PATH, file), sr=None)
        mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13).T
        mfcc = (mfcc - np.mean(mfcc)) / np.std(mfcc)
        X.append(mfcc)
        y_labels.append(label)


X_padded = pad_sequences(X, padding='post', dtype='float32')
y_labels = np.array(y_labels)

print("Input Shape:", X_padded.shape)
print("Labels:", y_labels)

X_train, X_test, y_train, y_test = train_test_split(X_padded, y_labels, test_size=0.25, random_state=42)

model = Sequential([
LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
Dropout(0.3),
LSTM(32),
Dense(16, activation='relu'),
Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.summary()

history = model.fit(
X_train, y_train,
epochs=30,
batch_size=2,
validation_data=(X_test, y_test)
)

plt.figure(figsize=(8,4))
plt.plot(history.history['accuracy'], label='Train Acc') 
plt.plot(history.history['val_accuracy'], label='Val Acc')
plt.legend()
plt.title('Accuracy Curve')
plt.show()

loss, acc = model.evaluate(X_test, y_test)
print('Test Accuracy:', acc)

def predict_audio(file_path):
    signal, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13).T
    mfcc = (mfcc - np.mean(mfcc)) / np.std(mfcc)
    mfcc = pad_sequences([mfcc], maxlen=X_padded.shape[1], padding='post')
    pred = model.predict(mfcc)[0][0]
    return 'YES' if pred > 0.5 else 'NO'

print(predict_audio('/kaggle/input/test12/Test/No-5.wav'))
print(predict_audio('/kaggle/input/test12/Test/yes-5.wav'))


'''
    return format_snippet(code)

def sp_cnn_code():
    code = '''
# CNN
import librosa
import librosa.display
import matplotlib.pyplot as plt
import os
import shutil
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout


audio_path = "/kaggle/input/speech-sounds/Sounds-speech/No-3.wav"
signal, sr = librosa.load(audio_path, sr=None)

plt.figure(figsize=(10,4))
librosa.display.waveshow(signal, sr=sr)
plt.title("Audio Waveform")
plt.xlabel("Time")
plt.ylabel("Amplitude")
plt.show()

print("Sampling Rate:", sr)
print("Duration (sec):", len(signal)/sr)


SOURCE_PATH = "/kaggle/input/speech-sounds/Sounds-speech"
DEST_PATH = "/kaggle/working/Sounds-speech"

os.makedirs(DEST_PATH, exist_ok=True)

for file in os.listdir(SOURCE_PATH):
    shutil.copy(os.path.join(SOURCE_PATH, file), DEST_PATH)


yes_folder = os.path.join(DEST_PATH, "Yes")
no_folder = os.path.join(DEST_PATH, "No")

os.makedirs(yes_folder, exist_ok=True)
os.makedirs(no_folder, exist_ok=True)

for file in os.listdir(DEST_PATH):
    if file.lower().startswith("yes") and file.endswith(".wav"):
        shutil.move(os.path.join(DEST_PATH, file), os.path.join(yes_folder, file))
    elif file.lower().startswith("no") and file.endswith(".wav"):
        shutil.move(os.path.join(DEST_PATH, file), os.path.join(no_folder, file))

print("Dataset copied and organized in /kaggle/working/")


DATASET_PATH = "/kaggle/working/Sounds-speech/"
classes = os.listdir(DATASET_PATH)

X = []
y = []

for label, class_name in enumerate(classes):
    class_path = os.path.join(DATASET_PATH, class_name)
    for file in os.listdir(class_path):
        file_path = os.path.join(class_path, file)
        signal, sr = librosa.load(file_path, duration=3)
        mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40)
        mfcc = mfcc.T
        X.append(mfcc)
        y.append(label)

print("Total Samples:", len(X))


X = pad_sequences(X, padding='post', dtype='float32')

X = X[..., np.newaxis]  

y = to_categorical(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("Training Shape:", X_train.shape)
print("Testing Shape:", X_test.shape)


model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=X_train.shape[1:]),
    MaxPooling2D((2,2)),
    Dropout(0.3),

    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D((2,2)),
    Dropout(0.3),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(len(classes), activation='softmax')
])

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=20,
    batch_size=32
)

test_loss, test_accuracy = model.evaluate(X_test, y_test)
print("Test Accuracy:", test_accuracy)

MAX_LEN = X_train.shape[1]
print("Fixed MFCC time steps:", MAX_LEN)



def predict_sound(file_path):
    signal, sr = librosa.load(file_path, duration=3)

    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40)
    mfcc = mfcc.T


    mfcc = pad_sequences(
        [mfcc],
        maxlen=MAX_LEN,
        padding='post',
        truncating='post',
        dtype='float32'
    )

    mfcc = mfcc[..., np.newaxis]

    prediction = model.predict(mfcc)
    predicted_class = classes[np.argmax(prediction)]
    return predicted_class

print("Predicted Sound:", predict_sound("/kaggle/input/test12/Test/yes-5.wav"))


'''
    return format_snippet(code)

def sp_hmm_code():
    code = '''
# HMM
import librosa
import numpy as np
import os
from hmmlearn import hmm

DATASET_PATH = "/content/drive/MyDrive/Audio_MNIST_data"

def extract_mfcc(file_path):
    signal, sr = librosa.load(file_path, sr=16000)

    signal = librosa.util.normalize(signal)
    signal, _ = librosa.effects.trim(signal)

    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=13)
    return mfcc.T

# collect training files
TARGET_DIGITS = ["0", "5"]
digit_files = {"0": [], "5": []}

for speaker in os.listdir(DATASET_PATH):
    speaker_path = os.path.join(DATASET_PATH, speaker)

    for file in os.listdir(speaker_path):
        if file.endswith(".wav"):
            digit = file.split("_")[0]
            if digit in TARGET_DIGITS:
                digit_files[digit].append(os.path.join(speaker_path, file))

# 30 samples per digit
for digit in digit_files:
    digit_files[digit] = digit_files[digit][:30]

hmm_models = {
    "0": hmm.GaussianHMM(n_components=5, covariance_type="diag", n_iter=100),
    "5": hmm.GaussianHMM(n_components=5, covariance_type="diag", n_iter=100)
}

def train_hmm(model, file_list):
    X = []
    lengths = []

    for file in file_list:
        mfcc = extract_mfcc(file)
        X.append(mfcc)
        lengths.append(len(mfcc))

    X = np.vstack(X)
    model.fit(X, lengths)

    return model

for digit in hmm_models:
    hmm_models[digit] = train_hmm(hmm_models[digit], digit_files[digit])

print(" training finished")

print(" testing...")
test_path = "blablabla2.wav"
test_features = extract_mfcc(test_path)

scores = {}

for digit, model in hmm_models.items():
    scores[digit] = model.score(test_features)

print("\n HMM SCORES")
for d, s in scores.items():
    print(f"Digit {d} => Score: {s}")

'''
    return format_snippet(code)

def sp_rule_code():
    code = '''
# Rule Based Analysis
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt

file_path = "blablabla.wav"

def preprocess_audio(file_path):
    signal, sr = librosa.load(file_path, sr=None)

    if sr != 16000:
        signal = librosa.resample(signal, orig_sr=sr, target_sr=16000)
        sr = 16000

    signal = librosa.util.normalize(signal)
    signal, _ = librosa.effects.trim(signal)

    return signal, sr

signal, sr = preprocess_audio(file_path)

energy = np.sum(signal ** 2) / len(signal)
zcr = np.mean(librosa.feature.zero_crossing_rate(signal))
spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=signal, sr=sr))

print("Energy:", energy)
print("ZCR:", zcr)
print("Spectral Centroid:", spectral_centroid)

# Energy Based Rule
if energy > 0.01:
    energy_label = "Strongly Spoken Digit"
else:
    energy_label = "Weakly Spoken Digit"

# ZCR Based Rule
if zcr > 0.1:
    zcr_label = "Unvoiced Dominant"
else:
    zcr_label = "Voiced Dominant"

# Spectral Centroid Rule
if spectral_centroid > 3000:
    spectral_label = "High Frequency Content"
else:
    spectral_label = "Low Frequency Content"

print("\nRULE BASED SPEECH ANALYSIS")
print("Energy Rule:", energy_label)
print("ZCR Rule:", zcr_label)
print("Spectral Rule:", spectral_label)

if energy > 0.01 and zcr < 0.1:
    print("Rule-Based Result: CLEAR VOICED DIGIT")
elif energy > 0.01 and zcr > 0.1:
    print("Rule-Based Result: NOISY / FAST DIGIT")
else:
    print("Rule-Based Result: UNCLEAR DIGIT")

'''
    return format_snippet(code)