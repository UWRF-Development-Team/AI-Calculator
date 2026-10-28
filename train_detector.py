import os
import keras
import json
import tensorflow as tf

from keras import layers, models, losses, optimizers

BASE_PATH = "training-data"
IMAGES = os.path.sep.join([BASE_PATH, "images"])
BOXES = os.path.sep.join([BASE_PATH, "data.json"])

OUTPUT_PATH = "output"
MODEL_PATH = os.path.sep.join([OUTPUT_PATH, "segmentor.h5"])

IMAGE_W = 640
IMAGE_H = 320

LR = 1e-4
EPOCHS = 20
BATCH_SIZE = 32
BOXES_PREDICT = 25

# this was originally 640, 320, 3 but our images are monochrome so we can reduce the input size
def build_model(convolves, input_shape=(320, 640, 1)):
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
    model.add(layers.Dense(BOXES_PREDICT*5, activation='sigmoid'))
    model.add(layers.Reshape((BOXES_PREDICT, 5)))

    return model

def image(filename):
    img = tf.io.read_file(os.path.sep.join([IMAGES, filename]))
    img = tf.io.decode_png(img, channels=1)
    img = tf.cast(img, tf.float32) / 255.0

    return img

def bbox_loss(true_y, pred_y):
    true_bboxes = true_y[..., :4]
    pred_bboxes = pred_y[..., :4]

    true_conf = true_y[..., 4]
    pred_conf = pred_y[..., 4]

    mask = true_conf

    bbox_error = tf.square(true_bboxes - pred_bboxes)
    bbox_error *= mask[..., tf.newaxis]

    bbox_loss = tf.reduce_sum(bbox_error) / tf.maximum(
        tf.reduce_sum(mask) * 4.0, 1.0
    )

    conf_loss = tf.reduce_mean(losses.binary_crossentropy(true_conf, pred_conf))

    return bbox_loss + conf_loss

# data preprocessing
data = json.load(open(BOXES))

for d in data:
    bounds = d["bounds"]
    for box in bounds:
        # some useful scrubbing, some training data might be old and doesn't have bbox confidence
        # we can add this and set it to 1 because obviously user-made bounding boxes are fully confident
        if not "confidence" in box:
            box["confidence"] = 1.0
    while len(bounds) < BOXES_PREDICT:
        # pad data with 0 confidence boxes so model can learn to output dummy boxes where no character is present
        bounds.append({"character": "", "start": [0, 0], "end": [0, 0], "confidence": 0.0})

# create feature and label sets
X = tf.stack([
    image(d["filename"]) for d in data
])

y = tf.constant([
    [
        [
            # x1, y1, x2, y2 (normalized to [0, 1]), confidence
            bound["start"][0] / IMAGE_W,
            bound["start"][1] / IMAGE_H,
            bound["end"][0] / IMAGE_W,
            bound["end"][1] / IMAGE_H,
            bound["confidence"]
        ] for bound in d["bounds"]
    ] for d in data
], dtype=tf.float32)

dataset = tf.data.Dataset.from_tensor_slices((X, y))
dataset = dataset.shuffle(buffer_size=len(X), seed=5)

# split data 80/20 train and test (since we wont get much of either lol)
train_size = int(0.8 * len(X))

train_dataset = dataset.take(train_size).batch(BATCH_SIZE)
test_dataset = dataset.skip(train_size).batch(BATCH_SIZE)

model = build_model(convolves=((16, 32)))
model.summary()

model.compile(
    optimizer=optimizers.Adam(learning_rate=LR),
    loss=bbox_loss
)

history = model.fit(
    train_dataset,
    validation_data=test_dataset,
    epochs=EPOCHS
)