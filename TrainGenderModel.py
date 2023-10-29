import os
import glob
import random
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    BatchNormalization, Conv2D, MaxPooling2D, Activation, Flatten, Dropout, Dense
)
from tensorflow.keras import backend as K

# Initialize hyperparameters
NUM_EPOCHS = 100
LEARNING_RATE = 1e-3
BATCH_SIZE = 64
IMAGE_DIMENSIONS = (96, 96, 3)

# Lists to store image data and their respective labels
image_data = []
image_labels = []

# Load image paths from the dataset directory
dataset_directory = r'C:\Files\GenderFaceDataset'
image_paths = [f for f in glob.glob(dataset_directory + "/**/*", recursive=True) if not os.path.isdir(f)]
random.shuffle(image_paths)

# Convert images to arrays and label them based on their category (man/woman)
for img_path in image_paths:
    image = cv2.imread(img_path)
    image = cv2.resize(image, (IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1]))
    image = img_to_array(image)
    image_data.append(image)

    # Extract label from the image path
    label = img_path.split(os.path.sep)[-2]
    label = 1 if label == "woman" else 0
    image_labels.append([label])

# Normalize image data to be between 0 and 1
image_data = np.array(image_data, dtype="float") / 255.0
image_labels = np.array(image_labels)

# Split the dataset into training and validation sets
(train_images, test_images, train_labels, test_labels) = train_test_split(
    image_data, image_labels, test_size=0.2, random_state=42
)

# Convert labels to one-hot encoded format
train_labels = to_categorical(train_labels, num_classes=2)
test_labels = to_categorical(test_labels, num_classes=2)

# Data augmentation configuration
data_augmentation = ImageDataGenerator(
    rotation_range=25, width_shift_range=0.1, height_shift_range=0.1,
    shear_range=0.2, zoom_range=0.2, horizontal_flip=True, fill_mode="nearest"
)

# Define the CNN model for gender classification
def build_cnn_model(width, height, depth, num_classes):
    model = Sequential()
    input_shape = (height, width, depth)
    channel_dimension = -1

    # Adjust input shape and channel dimension based on data format
    if K.image_data_format() == "channels_first":
        input_shape = (depth, height, width)
        channel_dimension = 1

    # Define the model layers
    # ... [The model layers remain unchanged]

    return model

# Build and compile the model
gender_model = build_cnn_model(
    width=IMAGE_DIMENSIONS[0], height=IMAGE_DIMENSIONS[1], depth=IMAGE_DIMENSIONS[2], num_classes=2
)
optimizer = Adam(lr=LEARNING_RATE, decay=LEARNING_RATE / NUM_EPOCHS)
gender_model.compile(loss="binary_crossentropy", optimizer=optimizer, metrics=["accuracy"])

# Train the model using the augmented data
training_history = gender_model.fit_generator(
    data_augmentation.flow(train_images, train_labels, batch_size=BATCH_SIZE),
    validation_data=(test_images, test_labels),
    steps_per_epoch=len(train_images) // BATCH_SIZE,
    epochs=NUM_EPOCHS, verbose=1
)

# Save the trained model
gender_model.save('gender_detection.model')

# Plot training and validation loss and accuracy
plt.style.use("ggplot")
plt.figure()
plt.plot(np.arange(0, NUM_EPOCHS), training_history.history["loss"], label="Training Loss")
plt.plot(np.arange(0, NUM_EPOCHS), training_history.history["val_loss"], label="Validation Loss")
plt.plot(np.arange(0, NUM_EPOCHS), training_history.history["accuracy"], label="Training Accuracy")
plt.plot(np.arange(0, NUM_EPOCHS), training_history.history["val_accuracy"], label="Validation Accuracy")
plt.title("Training Loss and Accuracy")
plt.xlabel("Epoch #")
plt.ylabel("Loss/Accuracy")
plt.legend(loc="upper right")
plt.savefig('training_plot.png')
