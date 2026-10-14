import tensorflow as tf
import os

from keras import layers, models

BASE_PATH = "training-data"
IMAGES = os.path.sep.join([BASE_PATH, "images"])
BOXES = os.path.sep.join([BASE_PATH, "data.json"])

OUTPUT_PATH = "output"
MODEL_PATH = os.path.sep.join([OUTPUT_PATH], "segmentor.h5")

LR = 1e-4
EPOCHS = 20
BATCH_SIZE = 32

# this was originally 640, 320, 3 but our images are monochrome so we can reduce the input size
def shape_model(input=(640,320,1)):
    inputs = layers.Input(shape=input)
    x = layers.Conv2D(16, (3, 3), activation='relu')(inputs)
    x = layers.MaxPool2D((2, 2))(x)
    
    model = models.Model(input=input, output=output)