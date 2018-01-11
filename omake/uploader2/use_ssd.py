import os
import numpy as np
from PIL import Image
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing.image import load_img, img_to_array, array_to_img
from ssd import SSD300
from ssd_utils import BBoxUtility

class UseSSD:

    def __init__(self):
        self.image_width = 300
        self.image_height = 300

        self.voc_classes = ['Aeroplane', 'Bicycle', 'Bird', 'Boat', 'Bottle',
                       'Bus', 'Car', 'Cat', 'Chair', 'Cow', 'Diningtable',
                       'Dog', 'Horse','Motorbike', 'Person', 'Pottedplant',
                       'Sheep', 'Sofa', 'Train', 'Tvmonitor']
        self.NUM_CLASSES = len(self.voc_classes) + 1

        self.model = SSD300((self.image_height, self.image_width, 3), num_classes=self.NUM_CLASSES)
        self.model.load_weights('weights_SSD300.hdf5', by_name=True)
        self.bbox_util = BBoxUtility(self.NUM_CLASSES)

    def normalize(self, img_array):
        return (img_array - np.mean(img_array)) / np.std(img_array) * 16 + 64

    def has_category(self, img_filepath, category_label_name, confidence):

        # 解析用
        with load_img(img_filepath, target_size=(self.image_height, self.image_width)) as img:
            img_array = img_to_array(img)
            img_array = self.normalize(img_array)

        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)

        preds = self.model.predict(img_array, batch_size=1, verbose=1)
        results = self.bbox_util.detection_out(preds)

        if len(results) <= 0:
            return

        det_label = results[0][:, 0]
        det_conf = results[0][:, 1]

        top_indices = [i for i, conf in enumerate(det_conf) if conf >= confidence]

        top_conf = det_conf[top_indices]

        top_label_indices = det_label[top_indices].tolist()

        for i in range(top_conf.shape[0]):
            label = int(top_label_indices[i])
            label_name = self.voc_classes[label - 1]

            if category_label_name == label_name:
                return True

        return False