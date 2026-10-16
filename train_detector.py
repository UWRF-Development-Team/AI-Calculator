import os
import keras

from keras import layers, models

BASE_PATH = "training-data"
IMAGES = os.path.sep.join([BASE_PATH, "images"])
BOXES = os.path.sep.join([BASE_PATH, "data.json"])

OUTPUT_PATH = "output"
MODEL_PATH = os.path.sep.join([OUTPUT_PATH, "segmentor.h5"])

LR = 1e-4
EPOCHS = 20
BATCH_SIZE = 32

# this was originally 640, 320, 3 but our images are monochrome so we can reduce the input size
def build_model(boxes_predict, convolves, input_shape=(320, 640, 1)):
    model = models.Sequential()

    model.add(layers.Input(shape=input_shape))

    for filters in convolves:
        model.add(layers.Conv2D(filters, (3, 3), activation='relu'))
        model.add(layers.BatchNormalization())
        model.add(layers.MaxPool2D((2, 2)))

    model.add(layers.GlobalAveragePooling2D())

    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dropout(0.3))

    # x1, y1, x2, y2, confidence 
    # (we're gonna kill low confidence boxes after prediction)
    model.add(layers.Dense(boxes_predict*5, activation='sigmoid'))
    model.add(layers.Reshape((boxes_predict, 5)))

    return model

model = build_model(25, (16, 32))
model.summary()