from keras import models
import numpy as np
from abc import ABC

class Model(ABC):
    def __init__(self, path):
        self.model = models.load_model(path, compile=False)

class Classifier(Model):
    def __init__(self):
        super().__init__("./classifier.keras")

    def crop(self, image, bounds):
        return np.asarray(image.crop([*bounds[:4]]))

    def predict(self, image):
        self.model.predict(image)
        # TODO return list of character confidences, maybe like dict or something with char as key

class Detector(Model):
    def __init__(self):
        super().__init__("./detector.keras")

    def predict(self, image):
        predicts = self.model.predict(image) 
        print(predicts.shape)
        predicts = predicts[predicts[:,:,4] > 0.1]
        newPreds = []
        for array in predicts:
            newPreds.append(np.multiply(array, np.asarray([640, 320, 640, 320, 1])).tolist())
        print(newPreds)
        return np.asarray(newPreds)
