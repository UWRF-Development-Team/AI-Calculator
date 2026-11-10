import tensorflow as tf

from keras import models

class Model:
    def __init__(self, path):
        self.model = models.load_model(path)
        self.model.summary()

class Classifier(Model):
    def __init__(self, path):
        super().__init__(path)

    def predict(self, image):
        self.model.predict(image)
        # TODO return list of character confidences, maybe like dict or something with char as key

class Detector(Model):
    def __init__(self, path):
        super().__init__(path)

    def predict(self, image):
        self.model.predict(image)
        # TODO return list of bounding box coords (denormalized to actual pixels) and confidence