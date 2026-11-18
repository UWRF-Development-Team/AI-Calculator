from PIL import Image, ImageOps
from keras import models
import numpy as np
from abc import ABC

class Model(ABC):
    def __init__(self, path):
        self.model = models.load_model(path, compile=False)

class Classifier(Model):
    def __init__(self):
        super().__init__("./classifier.keras")
        self.map = ["0","1","2","3","4","5","6","7","8","9","-","+","x","*","/","Λ"]

    def crop(self, image, bounds):
        return image.crop([*bounds[:4]])

    def predict(self, image):
        predict = self.model.predict(image)
        top = np.argsort(predict[0])[-5:][::-1]
        for i in top:
            print(
                f"Class {i} "
                f"({self.map[i]}): "
                f"{predict[0][i]:.4f}"
            )
        return self.map[int(np.argmax(predict))]


class Detector(Model):
    def __init__(self):
        super().__init__("./detector.keras")

    def predict(self, image):
        predicts = self.model.predict(image) 
        print(predicts.shape)
        predicts = predicts[predicts[:,:,4] > 0.8]
        newPreds = []
        for array in predicts:
            if array[0] > array[2] or array[1] > array[3]: continue
            newPreds.append(np.multiply(array, np.asarray([640, 320, 640, 320, 1])).tolist())
        # print(newPreds)
        return np.asarray(newPreds)

# Takes: A full-size PIL Image and crop coordinates
# Returns: The cropped, processed image
def process_image(full_image, crop_coords):
    image_segment = full_image.crop(crop_coords)
    image_segment = image_segment.convert("LA")  # Some are L, some are RGB
    image_segment.putalpha(255)

    pixel_data = image_segment.get_flattened_data()

    new_data = []
    for pixel in pixel_data:
        if pixel[0] == 255:
            new_data.append((255, 0))
        else:
            new_data.append(pixel)

    image_segment.putdata(new_data)

    image_segment = image_segment.crop(image_segment.getbbox(alpha_only=True))
    image_segment = image_segment.convert("L")

    image_segment.thumbnail((28, 28), Image.Resampling.LANCZOS)
    image_segment = ImageOps.expand(image_segment, 2, 255)
    image_segment = ImageOps.pad(image_segment, (32, 32), Image.Resampling.LANCZOS, color=255)

    pixel_data = image_segment.get_flattened_data()

    new_data = []
    for pixel in pixel_data:
        if pixel < 230:
            new_data.append(0)
        else:
            new_data.append(255)

    image_segment.putdata(new_data)
    image_segment.save("create_test.png")
    return image_segment
