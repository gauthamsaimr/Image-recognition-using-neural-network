import numpy as np
from captions_ref.config import Config
from captions_ref.dataset import prepare_single_test_data
from captions_ref.utils.vocabulary import Vocabulary
from captions_ref.model import CaptionGenerator
import tensorflow as tf
import os
from datetime import datetime
import base64

PATH_TO_IMAGES = './images/'
FINAL_MODEL = './captions_ref/models/289999.npy'

class API():
    def __init__(self):
        # Model Initialization code
        self.config = Config()
        self.config.beam_size = 3
        self.config.test_image_dir = PATH_TO_IMAGES
        self.config.phase = 'test'
        self.config.train_cnn = False

        self.vocabulary = Vocabulary(self.config.vocabulary_size,
                                     self.config.vocabulary_file)
        self.model = CaptionGenerator(self.config)

        self.sess = tf.Session()
        self.model.load(self.sess, FINAL_MODEL)

        tf.get_default_graph().finalize()

    def apply_model(self, input_file):
        """
        Should return JSON in the format of:
        {
            caption: "Caption text"
            success: True or False, based on running the application.
        }
        """
        image_filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".jpg"
        image_path = os.path.join(PATH_TO_IMAGES, image_filename)
        input_file.save(image_path)
        data, _ = prepare_single_test_data(self.config, image_path, self.vocabulary)
        print(data.image_files)
        caption = self.model.test_single(self.sess, data, self.vocabulary)
        #os.remove(image_path)

        return {'caption': caption, 'success': 'True' }

    def apply_model_b64(self, b64_image):
        """
        Should return JSON in the format of:
        {
            caption: "Caption text"
            success: True or False, based on running the application.
        }
        """
        image_filename = datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".jpg"
        image_path = os.path.join(PATH_TO_IMAGES, image_filename)
        input_file = open(image_path, "wb")
        input_file.write(base64.b64decode(b64_image))
        input_file.close()

        data, _ = prepare_single_test_data(self.config, image_path, self.vocabulary)
        print(data.image_files)
        caption = self.model.test_single(self.sess, data, self.vocabulary)
        # os.remove(image_path)

        return {'caption': caption, 'success': 'True'}
