import tensorflow as tf

from keras import models
from abc import ABC

class Model(ABC):
    def __init__(self, path):
        self.model = models.load_model(path)
        self.model.summary()

class Classifier(Model):
    def __init__(self):
        super().__init__("./classifier.keras")

    def predict(self, image):
        self.model.predict(image)
        # TODO return list of character confidences, maybe like dict or something with char as key

class Detector(Model):
    def __init__(self):
        super().__init__("./detector.keras")

    def predict(self, image):
        self.model.predict(image)
        # TODO return list of bounding box coords (denormalized to actual pixels) and confidence