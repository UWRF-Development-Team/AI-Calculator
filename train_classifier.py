import os
import pathlib

from PIL import Image, ImageChops, ImageOps
import keras
import json
import tensorflow as tf
import hasy_tools
import numpy as np

from keras import layers, models, losses, optimizers, metrics
from keras.src.utils import img_to_array


def create_local_dataset():
    images_path = "./training-data/images/"
    final_pil_images = []
    characters = []

    json_path = pathlib.Path("./training-data/data.json")
    with open(str(json_path), "r") as j:
        json_file = json.load(j)

    for image_data in json_file:
        full_image = Image.open(pathlib.Path(images_path + image_data["filename"]), "r")
        for segment in image_data["bounds"]:
            characters.append(segment["character"])

            image_segment = full_image.crop(segment["start"] + segment["end"])
            image_segment = image_segment.convert("RGBA") #Some are L, some are RGB
            image_segment.putalpha(255)

            bg = Image.new("RGBA", image_segment.size, "white")
            image_segment = ImageChops.difference(image_segment, bg)

            image_segment = image_segment.convert("L")

            image_segment.crop(image_segment.getbbox())
            image_segment.thumbnail((28, 28), Image.Resampling.LANCZOS)
            final_image = ImageOps.expand(image_segment, 2, 255)

            final_pil_images.append(img_to_array(final_image))

    dataset = tf.data.Dataset.from_tensor_slices([final_pil_images, characters]) # TODO I break :(
    dataset.shuffle(1e4)
    return dataset

create_local_dataset()

# this downloads it locally, so, y'know
# dont run this if you for some reason dont have 100MB free
# DATA = hasy_tools.load_data()
#
# IMAGE_W = 32
# IMAGE_H = 32
#
# LR = 1e-4
# EPOCHS = 10
# BATCH_SIZE = 32
#
#             #0   1   2   3   4   5   6   7   8   9
#             #leq geq  lt   gt   -    +    div  x
#             #*   [    ]    sqrt /    |    Λ
# WHITELIST = [70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
#             185, 186, 187, 188, 195, 196, 526, 549,
#             514, 918, 919, 960, 922, 920, 163]
#
#
# X_train = DATA['x_train']
# y_train = DATA['y_train'].squeeze()
# X_test = DATA['x_train']
# y_test = DATA['y_train'].squeeze()
#
# num_classes = len(WHITELIST)
#
# X_train_trim = X_train[np.isin(y_train, WHITELIST)]
# y_train_trim = y_train[np.isin(y_train, WHITELIST)]
# X_test_trim = X_test[np.isin(y_test, WHITELIST)]
# y_test_trim = y_test[np.isin(y_test, WHITELIST)]
#
# # because we want our targets to match the array bounds
# class_mapping = {original_id: new_id for new_id, original_id in enumerate(WHITELIST)}
# print(class_mapping)
#
# y_train_mapped = np.array([class_mapping[label] for label in y_train_trim])
# y_test_mapped = np.array([class_mapping[label] for label in y_test_trim])
#
# X_train_final = X_train_trim.astype("float32") / 255.0
# X_test_final = X_test_trim.astype("float32") / 255.0
#
#
# def build_model(convolves, input_shape=(32, 32, 1)):
#     model = models.Sequential()
#
#     model.add(layers.Input(shape=input_shape))
#
#     for filters in convolves:
#         model.add(layers.Conv2D(filters, (3, 3), activation='relu', padding='same'))
#         model.add(layers.BatchNormalization())
#         model.add(layers.MaxPool2D((2, 2), padding='same'))
#
#     model.add(layers.GlobalAveragePooling2D())
#     model.add(layers.Dropout(0.5))
#     model.add(layers.Dense(512, activation='relu'))
#     model.add(layers.Dropout(0.3))
#
#     model.add(layers.Dense(len(WHITELIST), activation='softmax'))
#     # model.add(layers.Reshape(len(WHITELIST)))
#
#     return model
#
# # dataset = trim_dataset(WHITELIST)
# # note symbol 163, uppercase lambda, which we will use for the caret ^
# # hasyv2 lacks this for some reason, in addition to the equals sign
# # but its not like we're gonna get a better dataset so we gotta cope
# model = build_model(convolves=(16, 32, 64, 128, 256))
# model.summary()
#
# # just guessing here that our dataset will have the labels encoded as a one-hot vector
# model.compile(
#     optimizer=optimizers.Adam(learning_rate=LR),
#     loss=losses.sparse_categorical_crossentropy,
#     metrics=['accuracy']
# )
#
# history = model.fit(
#     X_train_final,
#     y_train_mapped,
#     validation_data=[X_test_final, y_test_mapped],
#     epochs=EPOCHS
# )
#
# model.save("classifier.keras")