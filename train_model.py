import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, LSTM, Dense, Dropout, Bidirectional

import tensorflow as tf
print("🧠 TensorFlow version:", tf.__version__)
print("⚙️ GPUs:", tf.config.list_physical_devices('GPU'))

# Load
X = np.load("X_mitdb.npy")
y = np.load("y_mitdb.npy")

# Encode labels
le = LabelEncoder()
y_enc = le.fit_transform(y)
y_cat = to_categorical(y_enc)

# Save label classes for API
np.save("label_classes.npy", le.classes_)

# Reshape X
X = X.reshape((X.shape[0], X.shape[1], 1))

# Train/test split
X_train, X_val, y_train, y_val = train_test_split(X, y_cat, test_size=0.2, random_state=42)

# Build model
model = Sequential()
model.add(Conv1D(32, kernel_size=5, activation='relu', input_shape=(X.shape[1], 1)))
model.add(MaxPooling1D(pool_size=2))
model.add(Conv1D(64, kernel_size=5, activation='relu'))
model.add(MaxPooling1D(pool_size=2))
model.add(Bidirectional(LSTM(64)))
model.add(Dropout(0.4))
model.add(Dense(64, activation='relu'))
model.add(Dense(y_cat.shape[1], activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train
print("📦 Training ECG arrhythmia classifier...")
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_val, y_val))

# Save
model.save("ecg_model.h5")
print("✅ Model saved: ecg_model.h5")
