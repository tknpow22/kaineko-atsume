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

    def process_img(self, img_filepath, confidence, save_dirpath):

        # オリジナル
        with load_img(img_filepath) as img_orig:
            img_orig_array = img_to_array(img_orig)

        # オリジナル(解析用と同じ状態)
        img_orig_array_normalized = self.normalize(img_orig_array)

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
        det_xmin = results[0][:, 2]
        det_ymin = results[0][:, 3]
        det_xmax = results[0][:, 4]
        det_ymax = results[0][:, 5]

        top_indices = [i for i, conf in enumerate(det_conf) if conf >= confidence]

        top_conf = det_conf[top_indices]

        top_label_indices = det_label[top_indices].tolist()
        top_xmin = det_xmin[top_indices]
        top_ymin = det_ymin[top_indices]
        top_xmax = det_xmax[top_indices]
        top_ymax = det_ymax[top_indices]

        filename = os.path.basename(img_filepath)
        fname, ext = os.path.splitext(filename)

        for i in range(top_conf.shape[0]):
            label = int(top_label_indices[i])
            label_name = self.voc_classes[label - 1]

            print('%s: %.8f' % (label_name, top_conf[i]))

            xmin = int(round(top_xmin[i] * img_orig_array.shape[1]))
            ymin = int(round(top_ymin[i] * img_orig_array.shape[0]))
            xmax = int(round(top_xmax[i] * img_orig_array.shape[1]))
            ymax = int(round(top_ymax[i] * img_orig_array.shape[0]))


            acc = top_conf[i] * 100 // 10 * 10
            dir_name = '%s/%s/%02d_%02d' % (save_dirpath, label_name, acc, acc + 10)
            os.makedirs(dir_name, exist_ok=True)

            target_img_array = img_orig_array[ymin:ymax, xmin:xmax]
            with array_to_img(target_img_array) as target_img:
                target_img.save('%s/%s_%.8f.jpg' % (dir_name, fname, top_conf[i]))

            target_img_array_normalized = img_orig_array_normalized[ymin:ymax, xmin:xmax]
            with array_to_img(target_img_array_normalized) as target_img_normalized:
                target_img_normalized.save('%s/%s_%.8f_normalized.jpg' % (dir_name, fname, top_conf[i]))
