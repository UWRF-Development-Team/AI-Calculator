import os
import keras
import json
import tensorflow as tf

from keras import layers, models, losses, optimizers

BASE_PATH = "ocr-training-data"
# maybe! we just don't know yet
LABELS = os.path.sep.join([BASE_PATH, "data.json"])

OUTPUT_PATH = "output"
MODEL_PATH = os.path.sep.join([OUTPUT_PATH, "segmentor.h5"])

IMAGE_W = 32
IMAGE_H = 32

LR = 1e-4
EPOCHS = 20
BATCH_SIZE = 32
# we dont know this yet, but something around that, we could have this figured at runtime too probably
CHARACTER_CLASSES = 96

def build_model(convolves, input_shape=(32, 32, 1)):
    model = models.Sequential()

    model.add(layers.Input(shape=input_shape))

    for filters in convolves:
        model.add(layers.Conv2D(filters, (3, 3), activation='relu'))
        model.add(layers.BatchNormalization())
        model.add(layers.MaxPool2D((2, 2)))

    model.add(layers.GlobalAveragePooling2D())

    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dropout(0.3))

    model.add(layers.Dense(CHARACTER_CLASSES, activation='softmax'))
    model.add(layers.Reshape((CHARACTER_CLASSES)))

    return model

def image(filename):
    # once we have our character data, we can figure this path out
    # img = tf.io.read_file(os.path.sep.join([IMAGES, filename]))
    img = tf.io.decode_png(img, channels=1)
    img = tf.cast(img, tf.float32) / 255.0

    return img

model = build_model(convolves=(16, 32))
model.summary()

# just guessing here that our dataset will have the labels encoded as a one-hot vector
model.compile(
    optimizer=optimizers.Adam(learning_rate=LR),
    loss=losses.categorical_crossentropy
)

# history = model.fit(
#     train_dataset,
#     validation_data=test_dataset,
#     epochs=EPOCHS
# )