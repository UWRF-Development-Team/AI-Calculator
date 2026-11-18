import os
import pathlib

from PIL import Image
import keras
import json
import tensorflow as tf
import hasy_tools
import numpy as np
from matplotlib import pyplot as plt

from keras import layers, models, losses, optimizers, metrics

from models import process_image

            #0   1   2   3   4   5   6   7   8   9
            #-   +    ×
            #/     Λ
WHITELIST = [27, 28, 29, 30, 31, 32, 33, 34, 35, 36,
            112, 113, 132,
            272, 82]

# this downloads it locally, so, y'know
# dont run this if you for some reason dont have 100MB free
DATA = hasy_tools.load_data()

# for i, label in enumerate(DATA["labels"]):
    # print(i, label)

def create_local_dataset():
    images_path = pathlib.Path("./training-data/images/")
    json_path = pathlib.Path("./training-data/data.json")

    symbol_to_index = {
        str(DATA["labels"][original_id]): new_id
        for new_id, original_id in enumerate(WHITELIST)
    }

    X = []
    y = []

    with open(json_path, "r") as f:
        annotations = json.load(f)

    for image_data in annotations:
        image_path = images_path / image_data["filename"]

        with Image.open(image_path) as full_image:
            full_image.load()

            for segment in image_data["bounds"]:
                character = str(segment["character"])

                if character not in symbol_to_index:
                    continue

                start = segment["start"]
                end = segment["end"]

                crop_coords = (
                    start[0], start[1],
                    end[0], end[1]
                )

                image_segment = process_image(
                    full_image,
                    crop_coords
                )

                arr = np.asarray(
                    image_segment,
                    dtype=np.float32
                ) / 255.0

                arr = np.expand_dims(arr, axis=-1)

                X.append(arr)
                y.append(symbol_to_index[character])

    return (
        np.asarray(X, dtype=np.float32),
        np.asarray(y, dtype=np.int64)
    )

X_local, y_local = create_local_dataset()

indices = np.random.default_rng(42).permutation(len(X_local))

split = int(len(indices) * 0.8)

train_indices = indices[:split]
val_indices = indices[split:]

X_local_train = X_local[train_indices]
y_local_train = y_local[train_indices]

X_local_val = X_local[val_indices]
y_local_val = y_local[val_indices]

IMAGE_W = 32
IMAGE_H = 32

LR = 1e-4
EPOCHS = 10
BATCH_SIZE = 32

X_train = DATA['x_train']
y_train = DATA['y_train'].squeeze()
X_test = DATA['x_test']
y_test = DATA['y_test'].squeeze()

num_classes = len(WHITELIST)

X_train_trim = X_train[np.isin(y_train, WHITELIST)]
y_train_trim = y_train[np.isin(y_train, WHITELIST)]
X_test_trim = X_test[np.isin(y_test, WHITELIST)]
y_test_trim = y_test[np.isin(y_test, WHITELIST)]

# because we want our targets to match the array bounds
class_mapping = {original_id: new_id for new_id, original_id in enumerate(WHITELIST)}
print(class_mapping)

y_train_mapped = np.array([class_mapping[label] for label in y_train_trim])
y_test_mapped = np.array([class_mapping[label] for label in y_test_trim])

X_train_final = X_train_trim.astype("float32") / 255.0
X_test_final = X_test_trim.astype("float32") / 255.0

Image.fromarray(
    X_train_trim[0].squeeze()
).save("hasy_sample.png")


def build_model(convolves, input_shape=(32, 32, 1)):
    model = models.Sequential()

    model.add(layers.Input(shape=input_shape))

    for filters in convolves:
        model.add(layers.Conv2D(filters, (6, 6), activation='relu', padding='same'))
        model.add(layers.BatchNormalization())
        model.add(layers.MaxPool2D((2, 2), padding='same', strides=2))

    model.add(layers.GlobalAveragePooling2D())
    model.add(layers.Dense(128, activation='relu'))
    model.add(layers.Dense(128, activation='relu'))

    model.add(layers.Dense(len(WHITELIST), activation='softmax'))
    # model.add(layers.Reshape(len(WHITELIST)))

    return model

# dataset = trim_dataset(WHITELIST)
# note symbol 163, uppercase lambda, which we will use for the caret ^
# hasyv2 lacks this for some reason, in addition to the equals sign
# but its not like we're gonna get a better dataset so we gotta cope
model = build_model(convolves=(16, 32, 64, 128))
model.summary()

# just guessing here that our dataset will have the labels encoded as a one-hot vector
model.compile(
    optimizer=optimizers.Adam(learning_rate=LR),
    loss=losses.sparse_categorical_crossentropy,
    metrics=['accuracy']
)

history = model.fit(
    X_train_final,
    y_train_mapped,
    validation_data=[X_test_final, y_test_mapped],
    epochs=EPOCHS,
    shuffle=True
)

model.save("classifier.keras")