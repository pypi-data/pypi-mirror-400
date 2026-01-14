"""
SP Lab Code - Embedded Complete Notebook Code
==============================================

This module contains the complete code from all SP lab notebooks,
embedded as string constants for easy access via flowlab functions.

Lab 8: Speech Recognition with Rule-Based & Template Matching
Lab 9: HMM-Based Speech Recognition
Lab 10: CNN-Based Audio Digit Classification
Lab 11: LSTM-Based Audio Processing & Recognition
"""

LAB_CODE = {
    8: '''import os
import librosa
import numpy as np
from google.colab import drive

# 1. Setup Drive
drive.mount('/content/drive')
dataset_path = '/content/drive/MyDrive/Audio_Mnist'

temp_0_path = '/content/drive/MyDrive/Audio_Mnist/0/0_01_0.wav'
temp_1_path = '/content/drive/MyDrive/Audio_Mnist/1/1_02_0.wav'

# Load templates and get their MFCCs once
y0, _ = librosa.load(temp_0_path, duration=1)
y1, _ = librosa.load(temp_1_path, duration=1)
mfcc_temp0 = librosa.feature.mfcc(y=y0, sr=22050)
mfcc_temp1 = librosa.feature.mfcc(y=y1, sr=22050)

# 3. Main Loop through your folders
for folder_name in os.listdir(dataset_path):
    folder_path = os.path.join(dataset_path, folder_name)

    if os.path.isdir(folder_path):
        print(f"\\n--- Checking Folder: {folder_name} ---")

        for file_name in os.listdir(folder_path):
            if file_name.endswith('.wav'):
                file_path = os.path.join(folder_path, file_name)
                audio, sr = librosa.load(file_path, duration=1)

                # --- METHOD A: RULE BASED SYSTEM ---
                zcr = np.mean(librosa.feature.zero_crossing_rate(audio))
                if zcr > 0.1:
                    rule_result = "High Frequency (Hissy)"
                else:
                    rule_result = "Low Frequency (Smooth)"

                energy = np.sum(audio**2)/len(audio)
                if energy > 0.01:
                    energy_label = "loud sound detected"
                else:
                    energy_label = "Silent sound detected"

                if zcr > 0.1 and energy > 0.01:
                    print(f"File: {file_name} | Rule based: consonant heavy word")
                else:
                    print(f"File: {file_name} | Rule based: vowel dominant word")

                # --- METHOD B: TEMPLATE MATCHING (DTW) ---
                mfcc_current = librosa.feature.mfcc(y=audio, sr=sr)

                # Calculate distances
                dist0_matrix, _ = librosa.sequence.dtw(mfcc_current, mfcc_temp0)
                dist1_matrix, _ = librosa.sequence.dtw(mfcc_current, mfcc_temp1)

                # Get the final cost (bottom right of the matrix)
                score0 = dist0_matrix[-1, -1]
                score1 = dist1_matrix[-1, -1]

                # 6. FINAL RECOGNIZED WORD (DTW Matching)

                if score0 < score1:
                    recognized_word = "Zero"
                else:
                    recognized_word = "One"

                print(f"Scores -> 0: {score0:.2f}, 1: {score1:.2f}")
                print(f"*** FINAL RECOGNIZED WORD: {recognized_word} ***")
                print("-" * 30)''',

    9: '''!pip install hmmlearn
import os
import librosa
import numpy as np
from google.colab import drive
from hmmlearn import hmm

# 1. Setup
drive.mount('/content/drive')
base_path = '/content/drive/MyDrive/Audio_Mnist'

# --- EASY FEATURE LOADING FUNCTION ---
def get_folder_features(full_folder_path):
    all_mfccs = []

    # Get a list of all files in the folder
    file_list = os.listdir(full_folder_path)

    for file_name in file_list:
        if file_name.endswith('.wav'):
            # Step 1: Create the full path to the file
            file_path = os.path.join(full_folder_path, file_name)

            # Step 2: Load the audio
            audio, sr = librosa.load(file_path, duration=1)

            # Step 3: Extract MFCC and Transpose
            mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
            mfcc_T = mfcc.T

            # Step 4: Add to our list
            all_mfccs.append(mfcc_T)

    # Step 5: Stack all 50 samples into one big matrix for the HMM
    return np.vstack(all_mfccs)

# 2. TRAINING: Teach the HMM Digit 0 and Digit 1
print("Training models... please wait.")

# --- Train Model for Digit 0 ---
path_0 = os.path.join(base_path, '0')
features_0 = get_folder_features(path_0)

model_0 = hmm.GaussianHMM(n_components=5, covariance_type='diag', n_iter=100)
model_0.fit(features_0)

# --- Train Model for Digit 1 ---
path_1 = os.path.join(base_path, '1')
features_1 = get_folder_features(path_1)

model_1 = hmm.GaussianHMM(n_components=5, covariance_type='diag', n_iter=100)
model_1.fit(features_1)

print("Training Done!")

# 3. PREDICTION: Test a new file
test_file_path = os.path.join(base_path, '1/1_02_0.wav')
test_audio, _ = librosa.load(test_file_path, duration=1)
test_mfcc = librosa.feature.mfcc(y=test_audio, sr=22050, n_mfcc=13).T

# Get Log-Likelihood scores (Higher/Less negative is better)
score0 = model_0.score(test_mfcc)
score1 = model_1.score(test_mfcc)

# Final Result
print("\\n" + "="*30)
if score0 > score1:
    print(f"RECOGNIZED WORD: ZERO")
else:
    print(f"RECOGNIZED WORD: ONE")
print(f"Score 0: {score0:.2f} | Score 1: {score1:.2f}")
print("="*30)''',

    10: '''import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
from google.colab import drive
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input
from sklearn.model_selection import train_test_split

# 1. Mount Drive and Set Path
drive.mount('/content/drive')
dataset_path = '/content/drive/MyDrive/Audio_Mnist'

data = []
label = []

# 2. Data Loading
for folder in os.listdir(dataset_path):
    folder_path = os.path.join(dataset_path, folder)
    if os.path.isdir(folder_path):
        labels_value = int(folder)
        for file in os.listdir(folder_path):
            if file.endswith('.wav'):
                file_path = os.path.join(folder_path, file)

                # Load audio
                audio, sr = librosa.load(file_path, sr=None, duration=1)

                # Extract MFCCs (Full 2D representation for CNN)
                mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)

                # Transpose to get (Time, Features)
                mfcc_T = mfcc.T

                data.append(mfcc_T)
                label.append(labels_value)

# 3. Padding and Reshaping for CNN

X_padded = pad_sequences(data, padding='post', dtype='float32')

# CNNs need 4 dimensions: (Samples, Time, Features, Channels)
# We add the "1" channel at the end (like a grayscale image)
X = X_padded[..., np.newaxis]
Y = np.array(label)

# Train-Test Split
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# 4. CNN Model Architecture (From Lecture 10)
model = Sequential([
    Input(shape=(X.shape[1], X.shape[2], 1)),

    Conv2D(32, (3, 3), activation='relu', padding='same'),
    MaxPooling2D((2, 2)),

    Conv2D(64, (3, 3), activation='relu', padding='same'),
    MaxPooling2D((2, 2)),

    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.3),
    Dense(10, activation='softmax') # Assuming 10 digits (0-9)
])

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# 5. Training
history = model.fit(x_train, y_train, epochs=2, validation_data=(x_test, y_test), batch_size=32)

# 6. Evaluation & Plotting
loss, acc = model.evaluate(x_test, y_test)
print(f"Test Accuracy: {acc:.2f}")

plt.figure(figsize=(10, 5))
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Val Accuracy')
plt.title("CNN Training Accuracy by Sohail")
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

def prediction(file_path):
    audio, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
    mfcc_T = mfcc.T

    # 2. Normalize
    mfcc_normalize = (mfcc_T - np.mean(mfcc_T)) / np.std(mfcc_T)
    mfcc_padsequence = pad_sequences([mfcc_normalize], maxlen=X_padded.shape[1], padding='post')

    # Add the 4th dimension (the channel) so (1, 44, 13) becomes (1, 44, 13, 1)
    mfcc_for_cnn = mfcc_padsequence[..., np.newaxis]
    # -------------------

    # 4. Predict
    probabilities = model.predict(mfcc_for_cnn)[0]

    # 5. Get the class
    predicted_class = np.argmax(probabilities)
    return predicted_class

# Test it
file = '/content/drive/MyDrive/Audio_Mnist_data/01/0_01_0.wav'
print("Predicted Digit:", prediction(file))''',

    11: '''import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
from google.colab import drive
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

drive.mount('/content/drive')
dataset_path = '/content/drive/MyDrive/Audio_Mnist'

data = []
label = []

for folder in os.listdir(dataset_path):
    folder_path = os.path.join(dataset_path, folder)
    labels = int(folder)
    if os.path.isdir(folder_path):
        print(f"Processing Folder: {folder}")
        for files in os.listdir(folder_path):
            if files.endswith('.wav'):
                file_path = os.path.join(folder_path, files)
                audio, sr = librosa.load(file_path, sr = None, duration = 2)

                mfcc = librosa.feature.mfcc(y = audio, sr = sr, n_mfcc = 13)
                mfcc_transpose = mfcc.T
                mfcc_processed = (mfcc_transpose - np.mean(mfcc_transpose))/(np.std(mfcc_transpose))

                data.append(mfcc_processed)
                label.append(labels)

X_Padded = pad_sequences(data, padding = 'post' , dtype='float32')
Y = np.array(label)

print(f"X shape = {X_Padded.shape}, Y shape = {Y.shape}")

x_train, x_test, y_train, y_test = train_test_split(X_Padded, Y, test_size = 0.25, random_state = 42)

print(f"X_train_shape: {x_train.shape}, Y_train_shape: {y_train.shape}")
print(f"X_test_shape: {x_test.shape}, Y_test_shape: {y_test.shape}")

model = Sequential([
    LSTM(64, return_sequences = True, input_shape =(x_train.shape[1], x_train.shape[2])),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(16, activation = 'relu'),
    Dense(10, activation = 'softmax')
])

model.compile(optimizer = 'adam', loss = 'sparse_categorical_crossentropy', metrics = ['accuracy'])

model.summary()

history = model.fit(x_train, y_train, epochs = 20, batch_size = 2, validation_data =(x_test, y_test))

loss, acc = model.evaluate(x_test, y_test)
print("accuracy", acc)
print("loss", loss)

print(f"Final Accuracy: {acc:.2f}")
print(f"Final Loss: {loss:.2f}")

plt.figure(figsize=(8, 5))
plt.plot(history.history['accuracy'], label='Accuracy')
plt.plot(history.history['val_accuracy'], label='Val acc')
plt.title("Training Progress by Sohail")
plt.xlabel('Epoch (Round)')
plt.ylabel('Value')
plt.legend()
plt.show()

def prediction(file_path):
    audio, sr = librosa.load(file_path, sr = None)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc = 13)
    mfcc_T = mfcc.T
    mfcc_normalize = (mfcc_T - np.mean(mfcc_T))/np.std(mfcc_T)
    mfcc_padsequence = pad_sequences([mfcc_normalize], maxlen = X_Padded.shape[1] ,padding = 'post')

    # Predict probabilities for each class
    probabilities = model.predict(mfcc_padsequence)[0]
    # Get the class with the highest probability
    predicted_class = np.argmax(probabilities)
    return predicted_class

file= '/content/drive/MyDrive/Audio_Mnist_data/01/0_01_0.wav'
print("prediction of 1: " , prediction(file))''',
}
